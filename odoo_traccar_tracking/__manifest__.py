# -*- coding: utf-8 -*-
{
    'name': 'Odoo Traccar Tracking',
    'version': "19.0.1.0.0",
    'summary': 'Brief description of the module',
    'description': '''
        Detailed description of the module
    ''',
    'category': 'Uncategorized',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['base', 'mail','fleet'],
    'data': [
        'security/ir.model.access.csv',
        "views/odoo_traccar_tracking_views.xml",
        "views/traccar_device.xml",
        "views/res_config_settings.xml",
        "views/traccar_connection.xml"
    ],

    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}