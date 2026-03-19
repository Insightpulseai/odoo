# -*- coding: utf-8 -*-
{
    'name': 'IPAI Odoo Copilot',
    'version': '19.0.1.0.0',
    'summary': 'Odoo Copilot precursor — systray chat entry and agent gateway bridge',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'depends': ['base', 'web', 'mail', 'bus'],
    'data': [
        'security/copilot_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'views/copilot_assets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ipai_odoo_copilot/static/src/js/copilot_service.js',
            'ipai_odoo_copilot/static/src/js/copilot_systray.js',
            'ipai_odoo_copilot/static/src/xml/copilot_systray.xml',
            'ipai_odoo_copilot/static/src/css/copilot.css',
        ],
    },
    'installable': True,
    'application': False,
}
