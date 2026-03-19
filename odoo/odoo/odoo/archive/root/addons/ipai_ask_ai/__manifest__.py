# -*- coding: utf-8 -*-
{
    "name": "IPAI Ask AI",
    "version": "1.0.0",
    "category": "Productivity/AI",
    "summary": "AI chat agents with ChatGPT/Gemini provider toggles",
    "description": """
IPAI Ask AI
===========
AI chat agent integration with provider toggles for ChatGPT and Google Gemini.

Features:
* Enable/disable ChatGPT integration
* Enable/disable Google Gemini integration
* Secure API key storage (admin-only access)
* Settings UI integration
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/ai_settings_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
