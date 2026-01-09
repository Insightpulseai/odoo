# -*- coding: utf-8 -*-
{
    "name": "IPAI Theme TBWA (Backend)",
    "summary": "TBWA brand skin - Black chrome + Yellow accent + Clean surfaces",
    "description": """
IPAI Theme TBWA - Backend Branding
==================================

Applies TBWA corporate identity to Odoo backend:
- Black chrome (navbar/topbar)
- Yellow primary accent (#FFC400) for CTAs and active states
- Clean white/gray surfaces for ERP readability
- Consistent focus ring across all interactive elements

This is a standalone theme module with no complex dependencies.
Install this module to apply TBWA branding platform-wide.

Token Scheme:
- --tbwa-black: #0B0B0B (chrome)
- --tbwa-yellow: #FFC400 (primary accent)
- --bg: #F5F5F5 (background)
- --surface: #FFFFFF (cards)
- --border: #EAEAEA (borders)
    """,
    "version": "18.0.1.0.0",
    "category": "Themes/Backend",
    "license": "AGPL-3",
    "author": "InsightPulse AI / TBWA",
    "website": "https://insightpulseai.net",
    "depends": [
        "web",
    ],
    "data": [
        "views/assets.xml",
    ],
    "assets": {},
    "installable": True,
    "application": False,
    "auto_install": False,
}
