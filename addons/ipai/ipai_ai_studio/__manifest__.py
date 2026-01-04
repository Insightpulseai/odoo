# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Studio (CE) - AI-driven Module Builder",
    "version": "18.0.1.0.0",
    "summary": "AI-driven Studio-like module generator for Odoo CE (spec -> addon scaffold -> validate -> apply)",
    "category": "Productivity",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/ai_studio_menu.xml",
        "views/ai_studio_run_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "sequence": 10,
}
