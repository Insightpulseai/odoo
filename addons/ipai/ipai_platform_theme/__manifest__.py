# -*- coding: utf-8 -*-
{
    "name": "IPAI Platform Theme Tokens",
    "summary": "Core design tokens and theme infrastructure for IPAI platform",
    "description": """
IPAI Platform Theme Tokens
==========================

This module provides the foundational design tokens and theme infrastructure
that other IPAI theme modules depend on.

Features
--------
- CSS custom properties for colors, typography, spacing
- Theme switching support (light/dark mode)
- Shared tokens between Odoo and frontend applications
- Base styles for IPAI branding

Dependencies
------------
This module is required by:
- ipai_theme_tbwa_backend
- ipai_theme_fluent2 (optional enhancement)
- Other industry-specific theme modules

Usage
-----
This module is typically installed as a dependency. It provides:
- CSS variables under the ipai_platform_theme/static/src/css/ directory
- Theme switching JavaScript utilities
- Base SCSS mixins and functions
    """,
    "version": "18.0.1.0.0",
    "category": "Themes",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "web",
    ],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "ipai_platform_theme/static/src/css/tokens.css",
        ],
        "web.assets_frontend": [
            "ipai_platform_theme/static/src/css/tokens.css",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
