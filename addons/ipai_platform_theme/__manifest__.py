{
    "name": "IPAI Platform - Theme Tokens",
    "version": "18.0.1.0.0",
    "category": "Theme",
    "summary": "Design system tokens for IPAI platform",
    "description": """
IPAI Platform Theme Tokens
==========================

Provides a consistent design system across all IPAI modules.

Features:
- SCSS token system (spacing, colors, typography, shadows)
- Fiori-inspired design language
- Component token mapping
- Dark mode preparation (future)

The tokens are based on kb/design_system/tokens.yaml and provide
a modern SaaS look while maintaining Odoo backend compatibility.
    """,
    "author": "IPAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": ["web"],
    "data": [
        "views/assets.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_platform_theme/static/src/scss/tokens.scss",
            "ipai_platform_theme/static/src/scss/components.scss",
        ],
    },
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
