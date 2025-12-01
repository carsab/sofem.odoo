# -*- coding: utf-8 -*-
{
    'name': 'POS DIAN Partner Search',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Integración de búsqueda DIAN en ventana de asociados del POS',
    'description': '''
        Este módulo extiende la funcionalidad de búsqueda de asociados en el POS,
        permitiendo:
        
        - Búsqueda automática en DIAN al ingresar número de identificación (Enter)
        - Búsqueda avanzada con selección de tipo de documento
        - Integración con API DIAN a traves de Edipo de Jorels para obtener datos de clientes
        - Creación automática de asociados/clientes cuando no existen localmente
        - Indicador visual (badge) para asociados obtenidos desde DIAN
        - Compatible con módulo l10n_co_edi_jorels
        
        Uso:
        1. En POS, ir a búsqueda de clientes
        2. Escribir número de identificación y presionar Enter
        3. O hacer clic en "DIAN Search" para búsqueda avanzada
    ''',
    'author': 'Carlos Sabogal',
    'website': 'carsab@gmail.com',
    'license': 'LGPL-3',
    'depends': ['base','point_of_sale','l10n_co_edi_jorels',],
    'data': ['views/res_partner_views.xml',  ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_dian_partner_search/static/src/js/**/*.js',
            'pos_dian_partner_search/static/src/xml/**/*.xml',
            'pos_dian_partner_search/static/src/css/**/*.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}