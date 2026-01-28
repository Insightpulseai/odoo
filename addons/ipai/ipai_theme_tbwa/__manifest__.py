{
    "name": "IPAI Theme TBWA (Backend)",
    "version": "18.0.2.0.0",
    "summary": "TBWA brand skin for Odoo backend - overrides ipai_platform_theme tokens",
    "description": """
IPAI Theme TBWA (Backend)
=========================

TBWA brand skin that overrides ipai_platform_theme token values.
Does not define new tokens - only customizes brand slots.

Features:
---------
- Black chrome navbar/sidebar
- TBWA Yellow (#FFD800) accent color
- Clean white/gray surfaces
- Component-level styling for Odoo backend

Architecture:
-------------
This module ONLY overrides brand values from ipai_platform_theme:
- --ipai-brand-primary -> TBWA Yellow
- --ipai-brand-ink -> TBWA Black
- Component styles reference platform tokens

Dependencies:
- ipai_platform_theme (design system source of truth)

Author: InsightPulse AI / TBWA
License: LGPL-3
    """,
    "license": "LGPL-3",
    "author": "InsightPulse AI / TBWA",
    "website": "https://tbwa.com",
    "category": "Themes/Backend",
    "depends": [
        "web",
        "ipai_design_system_apps_sdk",
    ],
    "data": [
        "views/assets.xml",
    ],
    "assets": {},
    "installable": True,
    "application": False,
    "auto_install": False,
}
