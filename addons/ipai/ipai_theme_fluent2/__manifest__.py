# -*- coding: utf-8 -*-
{
    "name": "IPAI Fluent 2 Theme Tokens",
    "version": "18.0.1.1.0",
    "category": "Themes",
    "summary": "Microsoft Fluent 2 / Microsoft 365 Copilot design tokens for Odoo backend",
    "description": """
IPAI Fluent 2 Theme Tokens
==========================

This module injects Microsoft Fluent 2 design tokens as CSS custom properties
into the Odoo backend. It provides a consistent design language that can be
shared between Odoo and external applications (Next.js, Vite).

Features:
---------
- CSS custom properties from @fluentui/tokens (official)
- IPAI-prefixed semantic tokens for Odoo components
- Light and dark theme support via data-theme attribute
- System preference detection via prefers-color-scheme
- Shared tokens between Odoo and frontend applications
- JavaScript ThemeManager for dark mode toggling
- Complete Odoo component overrides (buttons, inputs, cards, lists, etc.)

Token Categories:
-----------------
- Colors: colorBrand*, colorNeutral*, colorStatus*, colorPalette*
- Typography: fontFamily*, fontSize*, fontWeight*, lineHeight*
- Spacing: spacing*, stroke*
- Shape: borderRadius*
- Shadows: shadow*
- Duration: duration*
- Curves: curve*

IPAI Token Categories:
----------------------
- --ipai-color-* (brand, neutral, semantic)
- --ipai-typography-* (font families, sizes, weights)
- --ipai-spacing-* (4-40px scale)
- --ipai-radius-* (none to pill)
- --ipai-shadow-* (sm to 2xl, elevation 02-64)
- --ipai-component-* (button, input, card, badge, nav, list, kanban, toast)

Usage:
------
Reference tokens in CSS/SCSS:
    background: var(--colorBrandBackground);
    color: var(--colorNeutralForeground1);
    border-radius: var(--borderRadiusMedium);

IPAI tokens:
    background: var(--ipai-component-button-primary-bg);
    color: var(--ipai-color-neutral-fg);
    border-radius: var(--ipai-radius-md);

Theme switching (JavaScript):
    IpaiThemeManager.toggleTheme();
    IpaiThemeManager.applyTheme('dark');

Documentation:
--------------
- Fluent 2: https://fluent2.microsoft.design/design-tokens
- Token Map: docs/ODOO_COPILOT_THEME_TOKEN_MAP.md
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
            "ipai_theme_fluent2/static/src/css/tokens.css",
            "ipai_theme_fluent2/static/src/css/theme.css",
            "ipai_theme_fluent2/static/src/js/theme.js",
        ],
        # Also load into frontend/website if website module is installed
        "web.assets_frontend": [
            "ipai_theme_fluent2/static/src/css/fluent2.css",
            "ipai_theme_fluent2/static/src/css/tokens.css",
            "ipai_theme_fluent2/static/src/css/theme.css",
            "ipai_theme_fluent2/static/src/js/theme.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
