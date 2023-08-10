from odoo import api, models, fields


class Base(models.AbstractModel):
    _inherit = 'base'

    def write(self, vals):
        for record in self:
            try:
                if "suggest_mode_switch" not in vals and record.is_in_suggest_mode:
                    suggestion = record.env['suggest.suggestion'].create({
                    'res_model_id': self.env['ir.model']._get(self._name).id,
                    'res_id': record.id,
                    'suggested_value': vals,
                    })
                    return super(Base, self).write({'suggestion_ids': [(4, suggestion.id)]})
            except AttributeError:
                pass
        return super(Base, self).write(vals)
    