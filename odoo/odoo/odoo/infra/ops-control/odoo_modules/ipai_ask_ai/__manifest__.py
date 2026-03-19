# -*- coding: utf-8 -*-
{
    'name': 'IPAI Ask AI - Copilot',
    'version': '18.0.1.0.0',
    'category': 'Productivity/AI',
    'summary': 'AI Copilot assistant for Odoo - Claude/ChatGPT-grade conversational UI',
    'description': """
IPAI Ask AI - Odoo Copilot
==========================

A modern AI assistant integrated into Odoo with:
- Global launcher (hotkey + systray button)
- Context-aware conversations (current model/record/view)
- Actionable responses (create/update records, navigate, schedule)
- Citations with record links and field diffs
- Safety rails with preview → apply workflow

Features:
---------
* Full OWL-based client action with side panel UI
* Real-time streaming responses
* Multiple interaction modes: Ask / Do / Explain
* Markdown rendering with syntax highlighting
* Action chips for quick operations
* Diff preview for write operations
* Citation links to Odoo records

Technical:
----------
* OWL 2.x components
* Integrates with ipai_platform_theme tokens
* WebSocket/polling for streaming
* Configurable AI backend endpoint
    """,
    'author': 'IPAI',
    'website': 'https://ipai.dev',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'ipai_platform_theme',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ipai_ask_ai_security.xml',
        'views/ask_ai_views.xml',
        'views/res_config_settings_views.xml',
        'data/ask_ai_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Services
            'ipai_ask_ai/static/src/js/services/ask_ai_service.js',
            'ipai_ask_ai/static/src/js/services/context_service.js',
            # Components
            'ipai_ask_ai/static/src/js/components/ask_ai_panel/ask_ai_panel.js',
            'ipai_ask_ai/static/src/js/components/ask_ai_panel/ask_ai_panel.xml',
            'ipai_ask_ai/static/src/js/components/ask_ai_panel/ask_ai_panel.scss',
            'ipai_ask_ai/static/src/js/components/message/message.js',
            'ipai_ask_ai/static/src/js/components/message/message.xml',
            'ipai_ask_ai/static/src/js/components/message/message.scss',
            'ipai_ask_ai/static/src/js/components/composer/composer.js',
            'ipai_ask_ai/static/src/js/components/composer/composer.xml',
            'ipai_ask_ai/static/src/js/components/composer/composer.scss',
            'ipai_ask_ai/static/src/js/components/action_chip/action_chip.js',
            'ipai_ask_ai/static/src/js/components/action_chip/action_chip.xml',
            'ipai_ask_ai/static/src/js/components/citation/citation.js',
            'ipai_ask_ai/static/src/js/components/citation/citation.xml',
            'ipai_ask_ai/static/src/js/components/diff_preview/diff_preview.js',
            'ipai_ask_ai/static/src/js/components/diff_preview/diff_preview.xml',
            'ipai_ask_ai/static/src/js/components/diff_preview/diff_preview.scss',
            # Widgets
            'ipai_ask_ai/static/src/js/widgets/systray_item/systray_item.js',
            'ipai_ask_ai/static/src/js/widgets/systray_item/systray_item.xml',
            'ipai_ask_ai/static/src/js/widgets/systray_item/systray_item.scss',
            # Client action
            'ipai_ask_ai/static/src/js/client_action/ask_ai_action.js',
            'ipai_ask_ai/static/src/js/client_action/ask_ai_action.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
