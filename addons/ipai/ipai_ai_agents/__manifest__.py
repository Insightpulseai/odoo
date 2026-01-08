# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Agents (CE/OCA 18)",
    "summary": "Odoo 19-style Ask AI / AI agents UX for Odoo CE 18 (OCA-friendly custom addon)",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/ai_agents_rules.xml",
        "views/agent_views.xml",
        "views/source_views.xml",
        "views/thread_views.xml",
        "views/menu.xml",
        "data/agent_data.xml",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
    "application": True,
    "installable": True,
}
