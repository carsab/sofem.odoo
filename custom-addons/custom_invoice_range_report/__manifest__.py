# custom_invoice_range_report/__manifest__.py
{
    'name': 'Reporte Primera y Última Factura por Rango',
    'version': '17.0.3.0',
    'summary': 'Reporte de primera/última factura por Punto de Venta/Diario en un rango de fechas, con exportación.',
    'description': """
        Permite seleccionar un rango de fechas y genera un reporte mostrando
        la primera y última factura emitida en ese período, agrupada por
        Punto de Venta (PoS Config) y Diario Contable.
        Ofrece visualización en pantalla con enlaces y descarga en PDF, XLSX y CSV.
        Fecha actual para referencia: Mayo 1, 2025.
    """,
    'author': 'Carlos Sabogal',
    'category': 'Accounting/Reporting',
    'depends': [
        'account', 
        'report_xlsx', 
        'point_of_sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/invoice_first_last_range_wizard_views.xml',
        'views/invoice_first_last_range_report_line_views.xml',
        'report/report_definition.xml',
        'report/report_template_pdf.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
