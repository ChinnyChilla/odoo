from odoo import api, fields, models


class Users(models.Model):
    _inherit = "res.users"
    
    suggest_mode_switch = fields.Boolean(string="Suggest Mode", store=True, readonly=False, default=False)
    
    def switch_suggest_mode(self):
        for users in self:
            users.sudo().action_switch_suggest_mode()
    
    def action_switch_suggest_mode(self):
        self.suggest_mode_switch = not self.suggest_mode_switch

    def check_suggest_mode(self):
        return self.suggest_mode_switch
    
    