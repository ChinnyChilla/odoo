from odoo import api, fields, models
import ast


class Suggestion(models.Model):
    _name = 'suggest.suggestion'
    _description = 'Suggestion'

    #model associated with the suggestion
    res_model_id = fields.Many2one(
        'ir.model', 'Document Model',
        index=True, ondelete='cascade', required=True)
    res_model = fields.Char(
        'Related Document Model',
        index=True, related='res_model_id.model', compute_sudo=True, store=True, readonly=True)
    res_id = fields.Many2oneReference(string='Related Document ID', index=True, model_field='res_model')
    res_name = fields.Char(
        'Document Name', compute='_compute_res_name', compute_sudo=True, store=True,
        readonly=True)
    
    user_id = fields.Many2one('res.users', string='Suggestor', default=lambda self: self.env.user)
    # Contains vals_list of all the changed fields
    # field is just string of json
    suggested_value = fields.Char(string='Suggested Value', required=True)

    can_write = fields.Boolean(string="Can Write", compute='_compute_can_write')
    
    same_as_creator = fields.Boolean(string="User same as creator", compute='_compute_same_as_creator')

    date_created = fields.Datetime(string="Date created", default=fields.Datetime.now())

    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for suggestion in self:
            suggestion.res_name = suggestion.res_model and \
                self.env[suggestion.res_model].browse(suggestion.res_id).display_name

    @api.depends('res_model', 'res_id')
    def _compute_can_write(self):
        if self.env.user.suggest_mode_switch:
            self.can_write = False
            return  
        try:
            self.check_access_rule('write')
            self.can_write = True
            return
        except:
            self.can_write = False
            return
        
    @api.depends('res_model', 'res_id')
    def _compute_same_as_creator(self):
        if self.env.user == self.user_id:
            self.same_as_creator = True
        else:
            self.same_as_creator = False
    #might not need this
    def unlink(self):
        return super(Suggestion, self).unlink()

    def saveRecord(self):
        self.env[self.res_model].browse(self.res_id).write(ast.literal_eval(self.suggested_value))
        return self.unlink()
    
    def remove_edit(self, related_model_name, edit):
        self.ensure_one()
        data_suggestion = ast.literal_eval(self.suggested_value)
        data_suggestion[related_model_name].remove(edit)
        self.suggested_value = data_suggestion
        return
    # make sure all the ids are still valid
    def validate_edit(self, related_model, related_model_name, edit):
        self.ensure_one()
        if type(edit[1]) is int:
            testing = related_model.search([('id', '=', edit[1])])
            if (len(testing) == 0):
                self.remove_edit(related_model_name, edit)
                raise ValueError("ID missing")

    def format_edit_many(self, suggestion_id, model_fields, edit_field_name, edits):
        related_model = self.env[model_fields[edit_field_name]['relation']]
        related_model_fields = related_model.fields_get()
        commands = {0: 'Add', 1: 'Modify', 2: 'Remove', 3: 'Unlink', 4:'Link', 5:'Clear', 6: 'Set'}
        formatted_edits = []
        for edit in edits:
            try:
                self.env['suggest.suggestion'].browse(suggestion_id).validate_edit(related_model, edit_field_name, edit)
            except ValueError:
                return False
            # No changes to line
            if edit[0] == 4 and edit[2] == False:
                continue

            additional_values = []
            if type(edit[2]) == dict:
                temp_id = 0
                for sub_edit in edit[2]:
                    try:
                        related_model_field_string = related_model_fields[sub_edit]['string']
                    except:
                        continue
                    additional_values.append({
                        'string': related_model_field_string,
                        'value': edit[2][sub_edit],
                        'id': temp_id,
                    })
                    temp_id += 1
        # getting correct value
            if edit[0] in [1,2]:
                value = related_model.search([('id', '=', edit[1])])[0]['display_name']
            elif edit[0] in [5,6]:
                value = ", ".join([related_model.search([('id', '=', model_id)])[0]['display_name'] for model_id in edit[2]])
            else:
                try:
                    value = edit[2]['name']
                except:
                    value = "line"
            formatted_edits.append({
                'string': value,
                'command': commands[edit[0]],
                'value': model_fields[edit_field_name]['string'],
                'additional_value': additional_values
            })
        return formatted_edits

    def format_edit_one(self, suggestion_id, model_fields, edit_field_name, related_model_id ):
        related_model = self.env[model_fields[edit_field_name]['relation']]
        related_model_id = related_model.search([('id', '=', related_model_id)])
        return {
            'string': model_fields[edit_field_name]['string'],
            'command': 'Edit',
            'value': related_model_id['display_name'] if related_model_id else False,
        }
        
    def format_edit_string(self, suggestion_id, model_fields, edit_field_name, edit_value):
        return {
            'string': model_fields[edit_field_name]['string'],
            'command': 'Edit',
            'value': edit_value,
        }

    def format_suggestions(self):
        suggestions = self.read()
        formatted_suggestions = []
        for suggestion in suggestions:
            suggestion2 = {
                'id': suggestion['id'],
                'user_id': suggestion['user_id'],
                'can_write': suggestion['can_write'],
                'same_as_creator': suggestion['same_as_creator'],
                'date_created': suggestion['date_created'],
                'edits': []
            }
            try:
                suggestion_data = ast.literal_eval(suggestion['suggested_value'])
            except Exception as e:
                self.env['suggest.suggestion'].browse(suggestion['id']).unlink()
                continue
            
            model_fields = self.env[suggestion['res_model']].fields_get()
            
            for edit_field_name in suggestion_data:
                if model_fields[edit_field_name]['type'] in ['one2many', 'many2many']:
                    formatted_edits = self.format_edit_many(suggestion['id'], model_fields, edit_field_name, suggestion_data[edit_field_name])
                    if not formatted_edits:
                        continue
                    suggestion2['edits'].extend(formatted_edits)
                elif model_fields[edit_field_name]['type'] == 'many2one':
                    formatted_edit = self.format_edit_one(suggestion['id'], model_fields, edit_field_name, suggestion_data[edit_field_name])
                    if not formatted_edit:
                        continue
                    suggestion2['edits'].append(formatted_edit)
                else:
                    formatted_edit = self.format_edit_string(suggestion['id'], model_fields, edit_field_name, suggestion_data[edit_field_name])
                    if not formatted_edit:
                        continue
                    suggestion2['edits'].append(formatted_edit)
            if (len(suggestion2['edits']) > 0):
                formatted_suggestions.append(suggestion2)
            else:
                if (suggestion2['can_write'] == True):
                    self.env['suggest.suggestion'].browse(suggestion['id']).sudo().unlink()
        return formatted_suggestions

