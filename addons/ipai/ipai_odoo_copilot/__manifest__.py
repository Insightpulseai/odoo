# -*- coding: utf-8 -*-
{
    'name': 'Pulser for Odoo',
    'version': '19.0.1.1.1',
    'summary': 'Pulser assistant — systray chat entry and agent gateway bridge',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'depends': ['base', 'web', 'mail', 'bus'],
    'data': [
        'security/copilot_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/copilot_partner_data.xml',
        'views/copilot_audit_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ipai_odoo_copilot/static/src/js/copilot_systray.js',
            'ipai_odoo_copilot/static/src/xml/copilot_systray.xml',
            'ipai_odoo_copilot/static/src/scss/copilot.scss',
        ],
    },
    'installable': True,
    'application': False,
}
