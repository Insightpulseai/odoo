# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Copilot",
    "summary": "Ask AI buttons and sidebar for forms",
    "description": """
IPAI AI Copilot
===============

UI layer for AI assistant integration in Odoo forms:

- Smart "Ask AI" button on configured models
- Sidebar panel for AI conversations
- Context-aware prompting based on current record
- Tool binding for MCP integration

Architecture:
- Thin UI layer only - no business logic
- Delegates to ipai_ai_core for sessions
- Delegates to ipai_mcp_hub for tool context

Configuration:
1. Enable AI on models via System Parameters (ipai.allow_ai_on_models)
2. Add smart button to forms via mixin
3. Use sidebar for ongoing conversations
    """,
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_ai_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/copilot_views.xml",
        "data/ir_config_parameter_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ai_copilot/static/src/xml/copilot_button.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
