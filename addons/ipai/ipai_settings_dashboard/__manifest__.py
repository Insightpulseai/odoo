# -*- coding: utf-8 -*-
{
    "name": "IPAI Settings Dashboard",
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "Unified AI provider settings with Kapa RAG, OpenAI, and Gemini support",
    "description": """
IPAI Settings Dashboard
=======================

Consolidated settings dashboard for all AI provider configurations.

Supported Providers:
--------------------
- **Kapa RAG**: Enterprise knowledge base with retrieval-augmented generation
- **OpenAI / ChatGPT**: GPT-4, GPT-4 Turbo, GPT-4o models
- **Google Gemini**: Gemini Pro, Gemini Pro Vision models
- **Ollama**: Local LLM deployment (Llama, Mistral, etc.)

Features:
---------
- Unified settings page with TBWA-styled UI
- Multi-provider configuration with company-level defaults
- API key management with secure storage
- RAG knowledge base configuration
- Provider health check and connectivity test
- Usage statistics and token tracking

Settings Location:
------------------
Settings → IPAI → AI Settings Dashboard
    """,
    "author": "InsightPulse AI / TBWA",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_ai_core",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/menuitem.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_settings_dashboard/static/src/scss/settings_dashboard.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
