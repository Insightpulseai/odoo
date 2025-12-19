# -*- coding: utf-8 -*-
{
    "name": "IPAI Asset Checkout",
    "summary": "Equipment and asset checkout tracking (Cheqroom-style parity)",
    "description": """
IPAI Asset Checkout - Equipment Management
==========================================

Native Odoo implementation providing Cheqroom-style functionality:

* Asset registry with barcode/QR support
* Checkout/check-in workflows with approvals
* Reservation calendar
* Custody tracking and handover logs
* Maintenance scheduling
* Location tracking
* Kit management (grouped assets)
* Depreciation integration with Odoo accounting

This is a PARITY MODULE - it clones Cheqroom workflows natively
without external SaaS integration. See ADR-0001 for philosophy.
    """,
    "version": "18.0.1.0.0",
    "category": "Operations/Equipment",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "hr",
        "stock",
        "barcodes",
    ],
    "data": [
        "security/assets_security.xml",
        "security/ir.model.access.csv",
        "data/assets_sequence.xml",
        "data/assets_categories.xml",
        "views/asset_views.xml",
        "views/checkout_views.xml",
        "views/reservation_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
