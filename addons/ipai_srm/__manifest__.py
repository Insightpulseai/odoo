# -*- coding: utf-8 -*-
{
    "name": "IPAI Supplier Relationship Management",
    "summary": "Supplier lifecycle and performance management (SAP SRM/Ariba-style parity)",
    "description": """
IPAI Supplier Relationship Management
======================================

Native Odoo implementation providing SAP SRM/Ariba-style functionality:

* Supplier qualification and onboarding workflows
* Supplier scorecards with weighted KPIs
* Contract lifecycle management
* RFQ/RFP process management
* Supplier performance tracking
* Risk assessment and monitoring
* Compliance document management
* Spend analytics integration

This is a PARITY MODULE - it clones SAP SRM workflows natively
without external SaaS integration. See ADR-0001 for philosophy.
    """,
    "version": "18.0.1.0.0",
    "category": "Inventory/Purchase",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "purchase",
        "contacts",
    ],
    "data": [
        "security/srm_security.xml",
        "security/ir.model.access.csv",
        "data/srm_sequence.xml",
        "data/srm_kpi_categories.xml",
        "views/supplier_views.xml",
        "views/scorecard_views.xml",
        "views/qualification_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
