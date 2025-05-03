# custom_invoice_range_report/models/invoice_first_last_range_report_line.py
from odoo import models, fields, api, _

class InvoiceFirstLastRangeReportLine(models.TransientModel):
    _name = 'invoice.first.last.range.report.line'
    _description = 'Línea de Reporte Primera/Última Factura Rango (Vista)'
    # Orden por defecto en la vista de árbol
    _order = 'journal_id, user_id'

    # Relación con el wizard que generó esta línea
    wizard_id = fields.Many2one(
        'invoice.first.last.range.wizard',
        string="Asistente Origen",
        ondelete='cascade' # Si se borra el wizard, se borran sus líneas
    )
    # Campos para mostrar en la tabla
    journal_id = fields.Many2one(
        'account.journal',
        string="Punto de Venta (Diario)",
        readonly=True
    )
    user_id = fields.Many2one(
        'res.users',
        string="Vendedor",
        readonly=True
    )
    # Guardamos la referencia completa a la factura para poder navegar
    first_invoice_id = fields.Many2one(
        'account.move',
        string="Ref Primera Factura",
        readonly=True
    )
    first_invoice_name = fields.Char(
        string="Nro. Primera Factura",
        readonly=True
    )
    last_invoice_id = fields.Many2one(
        'account.move',
        string="Ref Última Factura",
        readonly=True
    )
    last_invoice_name = fields.Char(
        string="Nro. Última Factura",
        readonly=True
    )

    # Acción para abrir la factura (llamada desde botones en la vista tree)
    def action_open_invoice(self):
        self.ensure_one()
        # El ID de la factura a abrir se pasa en el contexto desde el botón XML
        invoice_id_to_open = self.env.context.get('invoice_id_to_open')

        if not invoice_id_to_open:
             # Fallback por si acaso, aunque no debería ocurrir con el contexto bien puesto
             invoice_id_to_open = self.first_invoice_id.id or self.last_invoice_id.id

        if not invoice_id_to_open:
             raise UserError(_("No se pudo determinar qué factura abrir."))

        # Devolver la acción para abrir la vista form de la factura seleccionada
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice_id_to_open,
            'view_mode': 'form',
            'views': [(False, 'form')], # Especificar vista form
            'target': 'current', # Abrir en la ventana principal, reemplazando la lista
            # 'target': 'new', # Descomentar para abrir en un popup/modal
        }