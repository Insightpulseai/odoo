# -*- coding: utf-8 -*-
{
    'name': 'IPAI Ask AI - Chatter Integration',
    'version': '18.0.1.0.0',
    'category': 'Productivity/AI',
    'summary': 'Context-aware AI entry points in chatter, forms, and lists',
    'description': """
IPAI Ask AI - Chatter Integration
=================================

Adds "Ask AI" entry points throughout Odoo:
- Chatter: Button to ask about the current record
- Form views: Context menu option
- List views: Bulk action for selected records
- Field hover: Quick explain option

Features:
---------
* Automatic context capture (model, record, view)
* Selected records pass-through for bulk operations
* Integration with mail.thread models
* Quick action buttons in form header
    """,
    'author': 'IPAI',
    'website': 'https://ipai.dev',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'ipai_ask_ai',
    ],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'ipai_ask_ai_chatter/static/src/js/chatter_patch.js',
            'ipai_ask_ai_chatter/static/src/js/form_controller_patch.js',
            'ipai_ask_ai_chatter/static/src/js/list_controller_patch.js',
            'ipai_ask_ai_chatter/static/src/js/ask_ai_button/ask_ai_button.js',
            'ipai_ask_ai_chatter/static/src/js/ask_ai_button/ask_ai_button.xml',
            'ipai_ask_ai_chatter/static/src/js/ask_ai_button/ask_ai_button.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
