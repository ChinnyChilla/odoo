from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class MailActivity(models.AbstractModel):
    _name = 'mail.activity.mixin'
    _inherit = 'mail.activity.mixin'

    suggestion_ids = fields.Many2many(comodel_name='suggest.suggestion', string='Suggestions', groups="base.group_user")        #Here as well
    
    is_in_suggest_mode = fields.Boolean(string="Is In Suggest Mode", compute="_compute_suggest_mode", readonly=True)

    def _compute_suggest_mode(self):
        for users in self:
            users.is_in_suggest_mode = users.env.user.suggest_mode_switch

    def check_suggest_mode(self):
        return self.is_in_suggest_mode

    def check_inherit(self):
        model = ''.join(self.ids)
        if 'suggestion_ids' in self.env[model]._fields:
            pass
        else:
            print("newly suggestion mixin entered")
            raise ValidationError("Model does not support suggestions")
    