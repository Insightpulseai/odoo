# -*- coding: utf-8 -*-
{
    "name": "DEPRECATED: IPAI ChatGPT App SDK Theme",
    "version": "19.0.1.0.0",
    "category": "Themes",
    "summary": "DEPRECATED - Use ipai_design_system_apps_sdk instead. Do not install.",
    "description": """
IPAI ChatGPT App SDK Theme
==========================

This module provides a unified design token system that aligns the Odoo
backend and portal interfaces with the ChatGPT App SDK design language.

Features:
---------
- CSS custom properties (design tokens) as single source of truth
- Backend UI styling for /web
- Portal UI styling for /my
- AI widget overrides that consume design tokens
- Clean, modern aesthetic with subtle shadows and rounded corners

Design Tokens:
--------------
All tokens are defined as CSS custom properties in :root:
- --ipai-font-sans: System font stack
- --ipai-radius: Border radius (12px)
- --ipai-bg/--ipai-fg: Background and foreground colors
- --ipai-primary: Primary action color
- --ipai-shadow: Subtle shadow system
- See tokens.scss for complete list

Usage:
------
After installing this theme, all IPAI widgets and components should
reference var(--ipai-*) tokens instead of hardcoded values.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    "depends": [
        "web",
        "website",
    ],
    "data": [],
    "assets": {
        # Design tokens - loaded early so they're available everywhere
        "web._assets_primary_variables": [
            "ipai_chatgpt_sdk_theme/static/src/scss/primary_variables.scss",
        ],
        # Backend UI: tokens + backend overrides + widget overrides
        "web.assets_backend": [
            "ipai_chatgpt_sdk_theme/static/src/scss/tokens.scss",
            "ipai_chatgpt_sdk_theme/static/src/scss/backend.scss",
            "ipai_chatgpt_sdk_theme/static/src/scss/ai_widget_overrides.scss",
        ],
        # Portal/Website UI: tokens + portal overrides + widget overrides
        "website.assets_frontend": [
            "ipai_chatgpt_sdk_theme/static/src/scss/tokens.scss",
            "ipai_chatgpt_sdk_theme/static/src/scss/portal.scss",
            "ipai_chatgpt_sdk_theme/static/src/scss/ai_widget_overrides.scss",
        ],
    },
    "installable": False,
    "application": False,
    "auto_install": False,
}
