# -*- coding: utf-8 -*-
{
    'name': "pos_sofem",
    'summary': "Validations and customizations  for POS ",
    'description': """Validation to prevent quantities in cero for order lines. Adjust for preselect electronic invoice in payment screen """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'point_of_sale',
    'version': '0.1',
    'depends': ['base','point_of_sale','l10n_co_edi_jorels_pos'],
    'assets': {
            'point_of_sale._assets_pos': [
                'pos_sofem/static/src/js/ProductScreen.js','pos_sofem/static/src/js/PaymentScreen.js',
            ]
        },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,    
}