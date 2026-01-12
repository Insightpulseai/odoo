{
    "name": "IPAI Platform Theme",
    "version": "18.0.1.3.0",
    "category": "Theme",
    "summary": "Single source of truth for IPAI design tokens and branding",
    "description": """
IPAI Platform Theme - Design System Foundation
===============================================

This module provides the core design system tokens for all IPAI modules.
It is the **single source of truth** for colors, typography, spacing,
shadows, and component styling.

Theme Variants:
- TBWA (Yellow + Black): Scout Analytics style
- Neutral (Gray): Professional colorless theme
- Dark Mode: Dark surfaces with light text

Key Principles:
- All brand colors are defined as CSS custom properties (variables)
- Theme variants override token values via body class
- No hex codes should be used directly in other IPAI modules

Token Categories:
- Brand colors (primary, ink, surface, border)
- Semantic colors (success, warning, error, info)
- Typography (font family, sizes, weights)
- Spacing scale
- Border radii and shadows
- Transitions and z-index layers

Usage in Other Modules:
- Add 'ipai_platform_theme' to depends
- Use var(--tbwa-primary) instead of hex colors
- Use var(--tbwa-radius-base) instead of hardcoded border-radius

Configuration:
- Go to Settings > IPAI Theme to select theme variant
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": ["web"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/theme_inject.xml",
    ],
    "assets": {
        # Backend assets - full theme stack
        "web.assets_backend": [
            # 1. Core design tokens (foundation)
            "ipai_platform_theme/static/src/scss/tokens.scss",
            # 2. TBWA brand tokens (default theme)
            "ipai_platform_theme/static/src/scss/tbwa-tokens.scss",
            # 3. Theme variants (applied via body class)
            "ipai_platform_theme/static/src/scss/neutral-tokens.scss",
            "ipai_platform_theme/static/src/scss/dark-tokens.scss",
            # 4. Normalize (applies tokens to Odoo components)
            "ipai_platform_theme/static/src/scss/normalize.scss",
            # 5. TBWA component styling (full TBWA look)
            "ipai_platform_theme/static/src/scss/tbwa-components.scss",
            # 6. IPAI component extensions
            "ipai_platform_theme/static/src/scss/components.scss",
        ],
        # Frontend assets - same stack for website consistency
        "web.assets_frontend": [
            "ipai_platform_theme/static/src/scss/tokens.scss",
            "ipai_platform_theme/static/src/scss/tbwa-tokens.scss",
            "ipai_platform_theme/static/src/scss/neutral-tokens.scss",
            "ipai_platform_theme/static/src/scss/dark-tokens.scss",
            "ipai_platform_theme/static/src/scss/normalize.scss",
            "ipai_platform_theme/static/src/scss/tbwa-components.scss",
        ],
    },
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
