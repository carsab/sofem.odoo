# custom_invoice_range_report/__manifest__.py
{
    'name': 'Reporte Primera y Última Factura por Rango',
    'version': '17.0.1.0',
    'summary': 'Reporte de primera/última factura por punto de venta/vendedor en un rango de fechas, con exportación PDF/XLSX/CSV.',
    'description': """
        Permite seleccionar un rango de fechas y genera un reporte mostrando
        la primera y última factura emitida en ese período, agrupada por
        Diario (Punto de Venta) y Vendedor.
        Ofrece visualización en pantalla con enlaces y descarga en PDF, XLSX y CSV.
        Fecha actual para referencia: Mayo 1, 2025.
    """,
    'author': 'Tu Nombre/Empresa',
    'category': 'Accounting/Reporting',
    # Asegúrate de que 'report_xlsx' esté en tus addons e instalado
    'depends': ['account', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'views/invoice_first_last_range_wizard_views.xml',
        'views/invoice_first_last_range_report_line_views.xml',
        'report/report_definition.xml', # Definiciones de reportes
        'report/report_template_pdf.xml', # Plantilla PDF
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}