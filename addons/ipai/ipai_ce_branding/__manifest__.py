# -*- coding: utf-8 -*-
{
    "name": "InsightPulse AI - CE Branding",
    "version": "18.0.1.2.0",
    "category": "Customization",
    "summary": "Custom branding for Odoo CE login and backend",
    "description": """
        Custom Branding for Odoo CE
        ============================

        This module provides custom branding for the Odoo Community Edition:
        - Custom login background image
        - SCSS-based styling (no inline styles)
        - Easy image replacement via SCSS variables

        Image Replacement:
        - Option A: Replace static/src/img/login_bg.svg with your image (keep filename)
        - Option B: Add your image and update $ipai-login-bg-url in login.scss
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": ["web", "base"],
    "data": [
        "views/ce_branding_views.xml",
        "views/assets.xml",
    ],
    "assets": {},
    "installable": True,
    "application": False,
    "auto_install": False,
}
