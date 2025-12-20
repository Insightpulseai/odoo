# -*- coding: utf-8 -*-
{
    "name": "IPAI Partner Pack",
    "summary": "Odoo Partner industry pack for implementation services and success packs.",
    "version": "18.0.1.0.0",
    "category": "Services/Partner",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "crm",
        "sale_management",
        "project",
        "hr_timesheet",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/service_pack_views.xml",
        "views/quote_calculator_views.xml",
        "views/implementation_views.xml",
        "views/menus.xml",
        "data/service_pack_data.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
