# -*- coding: utf-8 -*-
{
    "name": "IPAI Catalog Bridge",
    "summary": "Unity Catalog-like asset registry bridge for Odoo ↔ Supabase sync",
    "description": """
IPAI Catalog Bridge
===================

Synchronizes Odoo models, actions, menus, and views to the Supabase catalog schema,
enabling unified governance, lineage tracking, and AI copilot tool discovery.

Features:
- Auto-register Odoo models as catalog assets
- Sync model fields and metadata to catalog
- Register Odoo actions for copilot tool bindings
- Provide catalog search and discovery APIs
- Support FQDN conventions for cross-system references

Architecture:
- catalog.assets: Universal asset registry
- catalog.tools: AI copilot tool definitions
- catalog.lineage_edges: Data lineage graph

FQDN Conventions:
- odoo.<db>.<model> → Odoo models
- odoo.<db>.action.<xmlid> → Odoo actions
- supabase.ipai.<schema>.<object> → Supabase tables/views
    """,
    "version": "18.0.1.0.0",
    "category": "InsightPulse/Technical",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_dev_studio_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/catalog_config.xml",
        "views/catalog_asset_views.xml",
        "views/catalog_menus.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
