# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Core",
    "version": "18.0.1.0.1",
    "category": "Productivity",
    "summary": "Provider-based AI threads/messages/citations for Odoo CE 18 (works with OCA AI UI).",
    "description": """
IPAI AI Core
============

Core AI infrastructure for Odoo CE 18 providing:

- Provider registry (active provider per company)
- Thread/message persistence
- Citation persistence and display
- Config UI for provider credentials
- OCA AI integration point (bridge pattern)

Features:
---------
- Multi-provider support (Kapa, OpenAI, Claude, etc.)
- Threaded conversations with context
- Citation tracking with source/snippet/URL
- Latency and confidence metrics
- RBAC for AI access

Usage:
------
1. Install ipai_ai_core and a provider module (e.g., ipai_ai_provider_kapa)
2. Configure provider in Settings -> AI Providers
3. Set active provider per company
4. Call env["ipai.ai.service"].ask(prompt) from code or use chatter integration
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": ["base", "mail", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/ipai_ai_menus.xml",
        "views/ipai_ai_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
