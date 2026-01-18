# -*- coding: utf-8 -*-
{
    "name": "IPAI Scout Bundle (Retail)",
    "summary": "One-click meta-installer for Scout retail intelligence vertical",
    "version": "18.0.1.0.0",
    "category": "InsightPulse/Vertical",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_scout_bundle",
    "license": "AGPL-3",
    "depends": [
        # CE core retail backbone
        "sale_management",
        "purchase",
        "stock",
        "stock_account",
        "point_of_sale",
        "account",

        # OCA governance baseline
        "base_tier_validation",
        "base_exception",
        "date_range",

        # IPAI bridge (the only custom code layer)
        "ipai_enterprise_bridge",
    ],
    # No data, no models - this is a pure meta-installer
    "data": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
