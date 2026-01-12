{
    "name": "IPAI Platform Theme",
    "version": "18.0.1.2.0",
    "category": "Theme",
    "summary": "Single source of truth for IPAI design tokens and branding",
    "description": """
IPAI Platform Theme - Design System Foundation
===============================================

This module provides the core design system tokens for all IPAI modules.
It is the **single source of truth** for colors, typography, spacing,
shadows, and component styling.

Key Principles:
- All brand colors are defined as CSS custom properties (variables)
- Skin modules (like ipai_theme_tbwa_backend) override values, not definitions
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
- Use var(--ipai-brand-primary) instead of hex colors
- Use var(--ipai-radius) instead of hardcoded border-radius

Odoo Integration:
- Maps IPAI tokens to --o-brand-primary and other Odoo variables
- Normalizes common Odoo components for consistent styling
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": ["web"],
    "assets": {
        # Backend assets - full TBWA theme stack
        "web.assets_backend": [
            # 1. Core design tokens (foundation)
            "ipai_platform_theme/static/src/scss/tokens.scss",
            # 2. TBWA brand tokens (overrides core with TBWA colors)
            "ipai_platform_theme/static/src/scss/tbwa-tokens.scss",
            # 3. Normalize (applies tokens to Odoo components)
            "ipai_platform_theme/static/src/scss/normalize.scss",
            # 4. TBWA component styling (full TBWA look)
            "ipai_platform_theme/static/src/scss/tbwa-components.scss",
            # 5. IPAI component extensions
            "ipai_platform_theme/static/src/scss/components.scss",
        ],
        # Frontend assets - same stack for website consistency
        "web.assets_frontend": [
            "ipai_platform_theme/static/src/scss/tokens.scss",
            "ipai_platform_theme/static/src/scss/tbwa-tokens.scss",
            "ipai_platform_theme/static/src/scss/normalize.scss",
            "ipai_platform_theme/static/src/scss/tbwa-components.scss",
        ],
    },
    "data": [],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
