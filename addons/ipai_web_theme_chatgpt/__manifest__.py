# -*- coding: utf-8 -*-
{
    "name": "IPAI Web Theme (ChatGPT-style)",
    "version": "18.0.1.0.0",
    "category": "Themes/Backend",
    "summary": "Brand tokens + UI polish for Odoo backend with ChatGPT-inspired design",
    "description": """
IPAI Web Theme (ChatGPT-style)
==============================

Applies a modern, ChatGPT-inspired design language to Odoo 18 backend.

Features:
- Global brand tokens (colors, radii, fonts, shadows)
- Modern navbar styling with purple primary color
- Rounded buttons and inputs with smooth hover states
- Card/kanban styling with subtle shadows and borders
- Pill/tag styling with full radius
- Improved list headers and control panels
- Focus ring styling for accessibility

Note: This theme only affects the backend (web client).
For website theming, use a separate website theme module.
    """,
    "author": "IPAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": ["web"],
    "data": [],
    # Odoo 18 native asset bundling (preferred over template inheritance)
    "assets": {
        "web.assets_backend": [
            # Design tokens must load first (variables for overrides)
            "ipai_web_theme_chatgpt/static/src/scss/tokens.scss",
            # Component overrides consume tokens
            "ipai_web_theme_chatgpt/static/src/scss/backend_overrides.scss",
        ],
    },
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
