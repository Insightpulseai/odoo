# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse AI - Foundry Connector',
    'version': '1.0.0',
    'category': 'Technical',
    'summary': 'Centralized connector for Azure Foundry and Document Intelligence',
    'author': 'InsightPulse AI',
    'depends': ['base', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ipai_foundry/static/src/scss/ipai_chat_widget.scss',
            'ipai_foundry/static/src/js/ipai_chat_widget.js',
            'ipai_foundry/static/src/xml/ipai_chat_widget.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
