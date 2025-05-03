# custom_invoice_range_report/report/report_xlsx.py
# Requiere: Módulo Odoo 'report_xlsx' (usualmente de OCA)
#           Librería Python 'xlsxwriter' (Odoo suele incluirla)

from odoo import models, _
from datetime import datetime # Para posible formato de fechas

class ReportInvoiceRangeXlsx(models.AbstractModel):
    # Nombre debe coincidir con report_name en report_definition.xml
    _name = 'report.custom_invoice_range_report.report_invoice_range_xlsx'
    _description = 'Reporte Primera/Última Factura XLSX'
    # Heredamos de la clase base de report_xlsx
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        # 'objects' usualmente es el recordset del modelo desde donde se llamó,
        # en nuestro caso, el wizard 'invoice.first.last.range.wizard'.
        # 'data' es el diccionario que pasamos en la llamada a report_action.

        report_data = data.get('report_data', [])
        date_start_str = data.get('date_start', '')
        date_end_str = data.get('date_end', '')

        # Nombre de la hoja de cálculo
        sheet = workbook.add_worksheet('Facturas por Rango')

        # --- Definición de Formatos (Opcional pero recomendado) ---
        bold = workbook.add_format({'bold': True})
        title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3', # Gris claro
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        cell_format = workbook.add_format({'border': 1}) # Borde simple para celdas de datos
        # Puedes añadir formatos para fechas, números, etc. si lo necesitas
        # date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})

        # --- Escritura del Contenido ---

        # Título del Reporte (fusionando celdas)
        sheet.merge_range('A1:H1', 'Reporte Primera y Última Factura', title_format)

        # Información del Rango de Fechas
        sheet.write('A3', 'Fecha Inicio:', bold)
        sheet.write('B3', date_start_str)
        sheet.write('D3', 'Fecha Fin:', bold)
        sheet.write('E3', date_end_str)

        # Cabeceras de la Tabla (en fila 5, índice 4)
        headers = [
            _("Punto de Venta (Diario)"),
            _("ID Diario"),
            _("Vendedor"),
            _("ID Vendedor"),
            _("Nro. Primera Factura"),
            _("ID Primera Factura"),
            _("Nro. Última Factura"),
            _("ID Última Factura")
        ]
        for col_num, header in enumerate(headers):
            sheet.write(4, col_num, header, header_format)

        # Escribir Datos de las Líneas (a partir de fila 6, índice 5)
        row_num = 5
        if report_data:
            for line in report_data:
                sheet.write(row_num, 0, line.get('journal_name', ''), cell_format)
                sheet.write(row_num, 1, line.get('journal_id'), cell_format)
                sheet.write(row_num, 2, line.get('user_name', ''), cell_format)
                sheet.write(row_num, 3, line.get('user_id'), cell_format)
                sheet.write(row_num, 4, line.get('first_invoice_name', ''), cell_format)
                sheet.write(row_num, 5, line.get('first_invoice_id'), cell_format)
                sheet.write(row_num, 6, line.get('last_invoice_name', ''), cell_format)
                sheet.write(row_num, 7, line.get('last_invoice_id'), cell_format)
                row_num += 1
        else:
            # Mensaje si no hay datos
            sheet.merge_range(f'A{row_num+1}:H{row_num+1}', _('No se encontraron datos para el período seleccionado.'), cell_format)

        # Ajustar Ancho de Columnas (opcional)
        sheet.set_column('A:A', 30) # Punto de Venta
        sheet.set_column('C:C', 30) # Vendedor
        sheet.set_column('E:E', 20) # Nro Factura
        sheet.set_column('G:G', 20) # Nro Factura
        sheet.set_column('B:B', 10) # IDs
        sheet.set_column('D:D', 10) # IDs
        sheet.set_column('F:F', 15) # IDs
        sheet.set_column('H:H', 15) # IDs

        # Nota: El libro de trabajo (workbook) se cierra y guarda automáticamente
        # por la clase base 'report.report_xlsx.abstract'. No necesitas llamar a workbook.close().