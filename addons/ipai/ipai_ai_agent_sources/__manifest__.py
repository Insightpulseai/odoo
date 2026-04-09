# -*- coding: utf-8 -*-
{
    "name": "AI Agent Sources",
    "version": "18.0.1.0.0",
    "summary": "Managed agent sources with lifecycle indexing — Odoo 18 Sources parity",
    "category": "Productivity/AI",
    "license": "LGPL-3",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/add_agent_source_wizard_views.xml",
        "views/ipai_ai_agent_source_views.xml",
        "views/ipai_ai_agent_views.xml",
    ],
    "installable": True,
    "application": False,
}
