# custom_invoice_range_report/models/invoice_first_last_range_report_line.py
from odoo import models, fields

class InvoiceFirstLastRangeReportLine(models.TransientModel):
    _name = 'invoice.first.last.range.report.line'
    _description = 'Línea de Reporte Primera/Última Factura Rango (Vista)'
    _order = 'pos_name, journal_id'

    wizard_id = fields.Many2one('invoice.first.last.range.wizard', string="Asistente Origen", ondelete='cascade')
    pos_name = fields.Char(string="Punto de Venta", readonly=True) 
    journal_id = fields.Many2one('account.journal', string="Diario", readonly=True)
    first_invoice_id = fields.Many2one('account.move', string="Ref Primera Factura", readonly=True)
    first_invoice_name = fields.Char(string="Nro. Primera Factura", readonly=True)
    last_invoice_id = fields.Many2one('account.move', string="Ref Última Factura", readonly=True)
    last_invoice_name = fields.Char(string="Nro. Última Factura", readonly=True)

    def action_open_invoice(self):
        self.ensure_one()
        invoice_id_to_open = self.env.context.get('invoice_id_to_open')
        if not invoice_id_to_open:
             return
        return {
            'type': 'ir.actions.act_window', 'res_model': 'account.move',
            'res_id': invoice_id_to_open, 'view_mode': 'form',
            'views': [(False, 'form')], 'target': 'current',
        }
