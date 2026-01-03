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
- Clean, product-style UI polish

Design System:
- Based on ChatGPT/modern SaaS visual language
- Purple primary (#6d28d9) accent color
- Neutral gray palette for text and borders
- Consistent 8px/12px/16px border radius system
- Subtle shadows for depth hierarchy

Installation:
1. Install this module
2. Clear browser cache and refresh with ?debug=assets
3. Enjoy the refreshed UI

Note: This theme only affects the backend (web client).
For website theming, use a separate website theme module.
    """,
    "author": "IPAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": ["web"],
    "data": [
        "views/assets.xml",
    ],
    "assets": {},
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
