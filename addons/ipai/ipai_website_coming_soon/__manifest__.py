# -*- coding: utf-8 -*-
{
    "name": "IPAI Website Coming Soon",
    "version": "19.0.1.0.0",
    "category": "Website",
    "summary": "Token-driven Coming Soon landing page with Pulser-style pulse indicator",
    "description": """
IPAI Website Coming Soon
========================

Replaces the production homepage with a brand-consistent Coming Soon landing
page while the full UI is being rebuilt.

Features
--------
- Token-driven CSS (references IPAI Design System SSOT variables)
- Pulser-style pulsating green indicator (CSS-only, no JS)
- Accessible: prefers-reduced-motion supported
- SEO: title, description, og:* meta tags via QWeb
- Mobile-first responsive layout
- Glass-morphism card on dark gradient background
- Does NOT modify global website theme; only overrides homepage route

Install / Rollback
------------------
Install: ``scripts/odoo_coming_soon_install.sh``
Rollback: ``scripts/odoo_coming_soon_rollback.sh``
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/InsightPulseAI/odoo",
    "license": "LGPL-3",
    "depends": [
        "website",
    ],
    "data": [
        "views/coming_soon_templates.xml",
        "data/website_page.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "ipai_website_coming_soon/static/src/scss/coming_soon.scss",
        ],
    },
    "post_init_hook": "_post_init_hook",
    "uninstall_hook": "_uninstall_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
