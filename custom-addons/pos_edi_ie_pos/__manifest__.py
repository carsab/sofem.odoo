# -*- coding: utf-8 -*-
{
    'name': 'PoS EDI Online Validation (CO)',
    'version': '17.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Adds an option to PoS config to enable/disable online DIAN validation for e-invoices.',
    'description': """
        This module extends the Point of Sale configuration to include a boolean field
        that determines if electronic invoices should be validated online with DIAN
        before printing. It adjusts the behavior of l10n_co_edi_jorels.
    """,
    'author': 'Tu Nombre/Empresa',
    'website': 'https://www.tuempresa.com',
    'depends': [
        'point_of_sale',
        'l10n_co_edi_jorels', # Asegúrate que este es el nombre técnico correcto del módulo
    ],
    'data': [
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_edi_ie_pos/static/src/js/pos_online_validation.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}