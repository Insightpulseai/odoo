# -*- coding: utf-8 -*-
{
    "name": "TBWA Backend Theme",
    "summary": "TBWA brand skin for Odoo backend (Yellow + Black)",
    "description": """
TBWA Backend Theme
==================

This module provides the TBWA brand skin for the Odoo backend.
It overrides the design tokens from `ipai_platform_theme` with
TBWA-specific brand values (Yellow #FFD800 + Black).

Architecture:
- ipai_platform_theme = design system source of truth (tokens, mappings)
- ipai_theme_tbwa_backend = TBWA skin that overrides those tokens

This module does NOT define new tokens, only overrides existing ones:
- --ipai-brand-primary: #FFD800 (TBWA Yellow)
- --ipai-brand-ink: #000000 (Black)
- --ipai-surface-canvas: #F5F5F5
- --ipai-surface-card: #FFFFFF

Key Features:
- Black navbar and sidebar chrome
- Yellow accent color for buttons, active states
- Scout Analytics / InsightPulse UI alignment
- Premium rounded corners (16px cards)
    """,
    "version": "18.0.1.3.0",
    "category": "Themes/Backend",
    "license": "LGPL-3",
    "author": "InsightPulse AI / TBWA Finance",
    "website": "https://insightpulseai.net",
    "depends": [
        "ipai_platform_theme",
    ],
    "excludes": [
        "web_enterprise",
    ],
    "assets": {
        # Load SCSS variables BEFORE Odoo/Bootstrap compiles
        "web._assets_primary_variables": [
            ("prepend", "ipai_theme_tbwa_backend/static/src/scss/variables.scss"),
        ],
        # Load token overrides and component styles AFTER platform theme
        "web.assets_backend": [
            "ipai_theme_tbwa_backend/static/src/scss/fonts.scss",
            "ipai_theme_tbwa_backend/static/src/scss/tbwa_tokens.scss",
            "ipai_theme_tbwa_backend/static/src/scss/backend.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
