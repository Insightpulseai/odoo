# -*- coding: utf-8 -*-
{
    "name": "TBWA Backend Theme",
    "summary": "TBWA branding skin - Black + Yellow + IBM Plex",
    "description": """
TBWA Backend Theme - Brand Skin
===============================

Applies TBWA corporate identity to Odoo backend.

This is a **skin module** that overrides ipai_platform_theme token values:
- TBWA Yellow (#FFD800) as primary accent
- Black navbar/sidebar
- IBM Plex Sans typography

Architecture:
- Depends on ipai_platform_theme (token source of truth)
- Sets TBWA-specific color values via CSS custom property overrides
- Contains SCSS variables for Odoo's Bootstrap/variable system
- Contains backend.scss for component-level overrides

DO NOT define new tokens here - only override existing ones.
    """,
    "version": "18.0.1.1.0",
    "category": "Themes/Backend",
    "license": "AGPL-3",
    "author": "InsightPulse AI / TBWA Finance",
    "website": "https://insightpulseai.net",
    "depends": [
        "web",
        "ipai_platform_theme",  # Token source of truth
    ],
    "excludes": [
        "web_enterprise",
    ],
    "assets": {
        # Primary variables - MUST load early to override Bootstrap/Odoo vars
        "web._assets_primary_variables": [
            (
                "after",
                "web/static/src/scss/primary_variables.scss",
                "ipai_theme_tbwa_backend/static/src/scss/variables.scss",
            ),
        ],
        # Backend assets - fonts, token overrides, UI tweaks (load after platform theme)
        "web.assets_backend": [
            "ipai_theme_tbwa_backend/static/src/scss/fonts.scss",
            "ipai_theme_tbwa_backend/static/src/scss/tbwa_tokens.scss",
            "ipai_theme_tbwa_backend/static/src/scss/backend.scss",
        ],
        # Dark mode overrides (optional)
        "web.assets_web_dark": [
            (
                "after",
                "ipai_theme_tbwa_backend/static/src/scss/variables.scss",
                "ipai_theme_tbwa_backend/static/src/scss/variables_dark.scss",
            ),
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
