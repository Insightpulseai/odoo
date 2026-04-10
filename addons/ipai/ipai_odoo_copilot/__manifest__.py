# -*- coding: utf-8 -*-
{
    'name': 'Pulser for Odoo',
    'version': '18.0.3.0.0',
    'summary': 'Pulser — AI assistant with systray chat, audit, rate limiting, and action dispatch',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'depends': ['base', 'web', 'mail', 'bus', 'ipai_knowledge_bridge'],
    'external_dependencies': {
        'python': [
            'requests',
        ],
    },
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
            'ipai_odoo_copilot/static/src/components/activity_timeline/activity_timeline.js',
            'ipai_odoo_copilot/static/src/components/activity_timeline/activity_timeline.xml',
            'ipai_odoo_copilot/static/src/components/activity_timeline/activity_timeline.scss',
            'ipai_odoo_copilot/static/src/components/chat_panel/chat_panel.js',
            'ipai_odoo_copilot/static/src/components/chat_panel/chat_panel.xml',
        ],
    },
    'installable': True,
    'application': False,
}
