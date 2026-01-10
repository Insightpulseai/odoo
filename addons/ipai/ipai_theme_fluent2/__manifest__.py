# -*- coding: utf-8 -*-
{
    "name": "IPAI Fluent 2 Theme Tokens",
    "version": "18.0.1.0.0",
    "category": "Themes",
    "summary": "Microsoft Fluent 2 design tokens for Odoo backend",
    "description": """
IPAI Fluent 2 Theme Tokens
==========================

This module injects Microsoft Fluent 2 design tokens as CSS custom properties
into the Odoo backend. It provides a consistent design language that can be
shared between Odoo and external applications (Next.js, Vite).

Features:
---------
- CSS custom properties from @fluentui/tokens
- Light and dark theme support via data-theme attribute
- System preference detection via prefers-color-scheme
- Shared tokens between Odoo and frontend applications

Token Categories:
-----------------
- Colors: colorBrand*, colorNeutral*, colorStatus*, colorPalette*
- Typography: fontFamily*, fontSize*, fontWeight*, lineHeight*
- Spacing: spacing*, stroke*
- Shape: borderRadius*
- Shadows: shadow*
- Duration: duration*
- Curves: curve*

Usage:
------
Reference tokens in CSS/SCSS:
    background: var(--colorBrandBackground);
    color: var(--colorNeutralForeground1);
    border-radius: var(--borderRadiusMedium);

Theme switching:
    document.documentElement.setAttribute('data-theme', 'dark');

Documentation:
--------------
https://fluent2.microsoft.design/design-tokens
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "web",
    ],
    "data": [],
    "assets": {
        # Load Fluent 2 tokens into backend assets
        "web.assets_backend": [
            "ipai_theme_fluent2/static/src/css/fluent2.css",
        ],
        # Also load into frontend/website if website module is installed
        "web.assets_frontend": [
            "ipai_theme_fluent2/static/src/css/fluent2.css",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
