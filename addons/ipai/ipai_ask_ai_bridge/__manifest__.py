# -*- coding: utf-8 -*-
{
    "name": "IPAI Ask AI Bridge",
    "summary": "Minimal launcher for external Ask AI / Copilot service.",
    "description": """
IPAI Ask AI Bridge
==================

A thin bridge module that launches an external Ask AI / Copilot service.

This module does NOT implement AI logic. It only:
- Adds a systray icon to launch the Copilot panel
- Provides settings to configure the external service URL
- Opens an iframe/popup to the external RAG service

All AI logic, prompts, and RAG processing live externally in:
- Supabase Edge Functions (RAG)
- Pulser AI Gateway (LLM routing)
- Spec Kit docs (prompt templates)

See: docs/architecture/ASK_AI_CONTRACT.md for the full contract.
    """,
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ask_ai_bridge/static/src/js/ask_ai_systray.js",
            "ipai_ask_ai_bridge/static/src/xml/ask_ai_systray.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
