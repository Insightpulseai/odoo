# -*- coding: utf-8 -*-
{
    "name": "IPAI Copilot Theme",
    "summary": "Fluent-style TBWA theme for Odoo 18 CE.",
    "description": """
IPAI Copilot Theme
==================

A thin theme module for visual alignment with Fluent UI + TBWA colors.

This module provides:
- Dark mode Copilot/Gemini-style neutral palette
- TBWA accent colors (#FFCC00)
- Fluent-style rounded corners and density
- Clean, minimal backend and portal styling

This module does NOT:
- Use Odoo Studio
- Add business logic
- Create database tables

Per the minimal stack policy, this is one of 4 allowed IPAI modules:
1. ipai_bir_compliance (BIR tax compliance)
2. ipai_finance_ppm (Finance PPM)
3. ipai_theme_copilot (this theme)
4. ipai_ask_ai_bridge (AI launcher)
    """,
    "version": "18.0.1.0.0",
    "category": "Theme/Backend",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        "web",
    ],
    "data": [
        "views/assets.xml",
    ],
    "assets": {},
    "installable": True,
    "application": False,
    "auto_install": False,
}
