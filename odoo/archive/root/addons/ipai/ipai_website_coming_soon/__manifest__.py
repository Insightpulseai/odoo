# -*- coding: utf-8 -*-
{
    "name": "IPAI Website Homepage",
    "version": "19.0.2.0.0",
    "category": "Website",
    "summary": "InsightPulseAI production homepage — Odoo-native Bootstrap, zero CSS deps",
    "description": """
IPAI Website Homepage
=====================

Production marketing homepage for insightpulseai.com / erp.insightpulseai.com.

Uses Odoo's native website.layout + Bootstrap 5 classes exclusively.
No custom SCSS, no external CSS variables — guaranteed to render correctly
the moment the module is installed.

Sections: Hero, What You Get, Products, Footer CTA.
Hides Odoo's default header/footer on the homepage via scoped template.

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
    "post_init_hook": "_post_init_hook",
    "uninstall_hook": "_uninstall_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
