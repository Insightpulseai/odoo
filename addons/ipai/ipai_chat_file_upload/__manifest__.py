# -*- coding: utf-8 -*-
{
    'name': 'IPAI Chat with File Upload',
    'version': '18.0.1.0.0',
    'summary': 'Managed source upload and source-grounded chat for Odoo copilot',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'depends': ['base', 'web', 'ipai_odoo_copilot'],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        'security/chat_groups.xml',
        'security/ir.model.access.csv',
        'views/chat_session_views.xml',
        'views/chat_source_views.xml',
        'views/chat_menus.xml',
    ],
    'installable': True,
    'application': False,
}
