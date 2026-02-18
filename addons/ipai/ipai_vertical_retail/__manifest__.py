# -*- coding: utf-8 -*-
# Copyright (C) InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).
{
    "name": "IPAI Vertical Retail (Scout)",
    "version": "19.0.1.0.0",
    "summary": "Retail/FMCG vertical layer for Scout on top of Odoo 18 CE + OCA.",
    "description": """
IPAI Vertical Retail (Scout)
============================

Retail/FMCG vertical layer providing:
- Store type classification (sari-sari, grocery, pharmacy, modern trade, HoReCa)
- Scout analytics integration fields on partners and products
- Product categorization for FMCG (dairy, snacks, beverage, tobacco, etc.)
- Regional and cluster tagging for Philippine market
- Competitor brand tracking

This module is part of the Scout retail analytics platform.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Verticals/Retail",
    "license": "AGPL-3",
    "depends": [
        "sale_management",
        "purchase",
        "stock",
        "account",
        "point_of_sale",
        "ipai_workspace_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/retail_product_categories.xml",
        "data/retail_store_tags.xml",
        "data/retail_pricelists.xml",
        "views/res_partner_views.xml",
        "views/product_template_views.xml",
    ],
    "demo": [
        "data/retail_demo_stores.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
