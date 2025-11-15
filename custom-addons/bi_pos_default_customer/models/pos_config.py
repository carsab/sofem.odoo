from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    res_partner_id = fields.Many2one('res.partner', string="default Customer")

