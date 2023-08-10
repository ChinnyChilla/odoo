from odoo import api, fields, models

from lxml import etree

class View(models.Model):
    _name = 'ir.ui.view'
    _inherit = 'ir.ui.view'


    is_in_suggest_mode = fields.Boolean(string="Is in Suggest Mode", compute="_compute_suggest_mode", readonly=True)

    def _compute_suggest_mode(self):
        if 'mail.activity.mixin' in self.env[self.model]._fields:
            if self.env.user.suggest_mode_switch:
                self.is_in_suggest_mode = True
            else:
                self.is_in_suggest_mode = False
        else:
            self.is_in_suggest_mode = False
            

class Model(models.AbstractModel):
    _inherit = 'base'
    def _get_view(self, view_id=None, view_type='form', **options):
        View = self.env['ir.ui.view'].sudo()

        # try to find a view_id if none provided
        if not view_id:
            # <view_type>_view_ref in context can be used to override the default view
            view_ref_key = view_type + '_view_ref'
            view_ref = self._context.get(view_ref_key)
            if view_ref:
                if '.' in view_ref:
                    module, view_ref = view_ref.split('.', 1)
                    query = "SELECT res_id FROM ir_model_data WHERE model='ir.ui.view' AND module=%s AND name=%s"
                    self._cr.execute(query, (module, view_ref))
                    view_ref_res = self._cr.fetchone()
                    if view_ref_res:
                        view_id = view_ref_res[0]
                else:
                    _logger.warning(
                        '%r requires a fully-qualified external id (got: %r for model %s). '
                        'Please use the complete `module.view_id` form instead.', view_ref_key, view_ref,
                        self._name
                    )

            if not view_id:
                # otherwise try to find the lowest priority matching ir.ui.view
                view_id = View.default_view(self._name, view_type)

        if view_id:
            # read the view with inherited views applied
            view = View.browse(view_id)
            
            has_sheet = etree.fromstring(view.arch).xpath("//sheet")
            if (view.type == 'form' and self._fields.get('suggestion_ids') and len(has_sheet) > 0):
                key = f'suggest.banner_view_{view_id}'
                banner_view = View.search([('key', '=', key)])
                if len(banner_view) == 0:
                    banner_view = View.create({
                        'name': f'suggest.banner_view_{view.name}',
                        'type': 'qweb',
                        'mode': 'extension',
                        'inherit_id': view_id,
                        'key': key,
                        'arch': """<xpath expr="//sheet" position="before" >
                                        <field name="is_in_suggest_mode" invisible="1"/>
                                        <div>
                                            <h2 class="o_edit_mode_banner" attrs="{'invisible': [('is_in_suggest_mode', '=', False)]}"> In Suggest Mode </h2>
                                        </div>
                                    </xpath>""",
                    })
                
                arch = banner_view._get_combined_arch()
            else:
                arch = view._get_combined_arch()
            
        else:
            # fallback on default views methods if no ir.ui.view could be found
            view = View.browse()
            try:
                arch = getattr(self, '_get_default_%s_view' % view_type)()
            except AttributeError:
                raise UserError(_("No default view of type '%s' could be found !", view_type))
        return arch, view


