# -*- coding: utf-8 -*-
{
    "name": "IPAI Fluent 2 Theme Tokens",
    "version": "19.0.1.0.0",
    "category": "Themes",
    "summary": "InsightPulse AI Multi-Aesthetic Theme System for Odoo (10 themes)",
    "description": """
IPAI Fluent 2 Theme System
===========================

This module provides the complete InsightPulse AI theme system with 5 aesthetic
systems and light/dark modes for Odoo backend, matching the design system used
in external applications (React, Next.js, Vite).

Theme System:
-------------
- 5 Aesthetic Systems: Default, Dull, Claude, ChatGPT, Gemini
- 2 Color Modes: Light and Dark
- Total: 10 distinct themes
- Live theme switcher in Odoo navbar (aesthetic dropdown + light/dark toggle)
- LocalStorage persistence for user preferences
- System dark mode detection and auto-switching

Features:
---------
- CSS custom properties from @fluentui/tokens (official)
- IPAI-prefixed semantic tokens for Odoo components
- Theme variables applied via data-aesthetic and data-color-mode attributes
- JavaScript ThemeSystemManager for programmatic theme control
- Complete Odoo component overrides (buttons, inputs, cards, lists, kanban, etc.)
- Shared tokens between Odoo and frontend applications
- Real-time theme switching without page reload

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
    "website": "https://insightpulseai.com",
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
            "ipai_theme_fluent2/static/src/css/theme-system.css",
            "ipai_theme_fluent2/static/src/js/theme.js",
            "ipai_theme_fluent2/static/src/js/theme-system.js",
        ],
        # Also load into frontend/website if website module is installed
        "web.assets_frontend": [
            "ipai_theme_fluent2/static/src/css/fluent2.css",
            "ipai_theme_fluent2/static/src/css/tokens.css",
            "ipai_theme_fluent2/static/src/css/theme.css",
            "ipai_theme_fluent2/static/src/css/theme-system.css",
            "ipai_theme_fluent2/static/src/js/theme.js",
            "ipai_theme_fluent2/static/src/js/theme-system.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
