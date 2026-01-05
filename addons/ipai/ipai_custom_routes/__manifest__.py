# -*- coding: utf-8 -*-
{
    "name": "InsightPulse Custom Routes",
    "version": "18.0.1.0.0",
    "category": "Extra Tools",
    "summary": "Clean URL routes for Odoo apps (/odoo/discuss, /odoo/invoicing, etc.)",
    "description": """
Custom Routes for Odoo Apps
============================

Provides clean URL routes matching official Odoo:
- /odoo/discuss → Discuss app
- /odoo/invoicing → Invoicing app
- /odoo/calendar → Calendar app
- /odoo/project → Project app
- /odoo/expenses → Expenses app

Also sets Apps Dashboard as default home page after login.

Features:
---------
* Clean URLs like official Odoo
* Apps Dashboard as default home page
* Compatible with Odoo 18 CE
* No manual configuration needed

Author: InsightPulse AI
License: AGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_custom_routes",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
        "mail",
        "calendar",
        "project",
        "hr_expense",
    ],
    "data": [
        "data/default_home_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
