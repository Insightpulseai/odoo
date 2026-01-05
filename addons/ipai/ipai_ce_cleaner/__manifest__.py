# -*- coding: utf-8 -*-
{
    "name": "IPAI CE Cleaner (No Enterprise/IAP)",
    "summary": "Hides Enterprise/IAP upsells and rewires links away from odoo.com.",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_ce_cleaner",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
        # OCA server-brand foundation (CE cleanup)
        "remove_odoo_enterprise",
        "disable_odoo_online",
    ],
    "data": [
        "views/ipai_ce_cleaner_views.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            ("prepend", "ipai_ce_cleaner/static/src/css/ipai_ce_cleaner.css"),
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
