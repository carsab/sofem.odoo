# custom_invoice_range_report/report/report_xlsx.py
from odoo import models, _

class ReportInvoiceRangeXlsx(models.AbstractModel):
    _name = 'report.custom_invoice_range_report.report_invoice_range_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Reporte Primera/Última Factura XLSX'

    def generate_xlsx_report(self, workbook, data, objects):
        report_data = data.get('report_data', [])
        date_start_str = data.get('date_start', '')
        date_end_str = data.get('date_end', '')

        sheet = workbook.add_worksheet('Facturas por Rango')
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
        cell_format = workbook.add_format({'border': 1})

        sheet.merge_range('A1:F1', 'Reporte Primera y Última Factura', bold)
        sheet.write('A3', 'Fecha Inicio:', bold)
        sheet.write('B3', date_start_str)

        headers = [
            _("Punto de Venta"), _("Diario"), _("ID Diario"),
            _("Nro. Primera Factura"), _("ID Primera Factura"),
            _("Nro. Última Factura"), _("ID Última Factura")
        ]
        for col_num, header in enumerate(headers):
            sheet.write(4, col_num, header, header_format)

        row_num = 5
        for line in report_data:
            sheet.write(row_num, 0, line.get('pos_name', ''), cell_format)
            sheet.write(row_num, 1, line.get('journal_name', ''), cell_format)
            sheet.write(row_num, 2, line.get('journal_id'), cell_format)
            sheet.write(row_num, 3, line.get('first_invoice_name', ''), cell_format)
            sheet.write(row_num, 4, line.get('first_invoice_id'), cell_format)
            sheet.write(row_num, 5, line.get('last_invoice_name', ''), cell_format)
            sheet.write(row_num, 6, line.get('last_invoice_id'), cell_format)
            row_num += 1
        
        sheet.set_column('A:B', 30)
        sheet.set_column('D:G', 20)
