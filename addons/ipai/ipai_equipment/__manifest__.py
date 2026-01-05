# -*- coding: utf-8 -*-
{
    "name": "IPAI Equipment Management",
    "summary": "Cheqroom-style equipment catalog, bookings, and incidents on Odoo CE + OCA.",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_equipment",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "maintenance",
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ipai_equipment_menus.xml",
        "views/ipai_equipment_views.xml",
    ],
    "installable": True,
    "application": False,  # Use ipai_assets as main entry point
    "auto_install": False,
}
