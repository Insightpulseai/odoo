# -*- coding: utf-8 -*-
{
    "name": "IPAI Fluent 2 Finance Theme",
    "summary": "Microsoft Fluent 2 Web design system for Finance PPM landing pages",
    "version": "18.0.1.0.0",
    "category": "Themes/Backend",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        "web",
        "ipai_finance_ppm",
    ],
    "data": [
        "views/assets.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_theme_fluent_finance/static/src/css/tokens.css",
            "ipai_theme_fluent_finance/static/src/css/finance_landing.css",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
