{
    'name': 'POS Colombian Resolution',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Adds resolution information to POS session closing report',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
        'l10n_co_edi_jorels',
    ],
    'data': [
        'views/report_saledetails.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'l10n_co_pos_resolution/static/src/js/sale_details_button_extension.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}