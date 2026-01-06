# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Provider: Kapa",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Kapa-style RAG provider for IPAI AI Core.",
    "description": """
IPAI AI Provider: Kapa
======================

Provides integration with Kapa-style RAG (Retrieval-Augmented Generation) APIs.

Features:
---------
- HTTP client for /api/chat endpoint
- Thread continuation support via /api/threads/{id}/chat
- Citation parsing and normalization
- Configurable base URL, API key, and project ID

Configuration:
--------------
1. Go to Settings -> IPAI Kapa Provider
2. Set Base URL (default: https://api.kapa.ai)
3. Set API Key
4. Set Project ID

The provider will be available for selection in AI Providers.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": ["ipai_ai_core"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
