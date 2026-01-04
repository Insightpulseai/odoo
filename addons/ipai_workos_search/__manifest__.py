# -*- coding: utf-8 -*-
{
    "name": "IPAI Work OS Search",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Global and scoped search for pages and databases",
    "description": """
        Search module providing Notion-like search:
        - Global search across pages, databases, and blocks
        - Scoped search within spaces or databases
        - Full-text search on block content
        - Quick search results with previews
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "AGPL-3",
    "icon": "fa-search",
    "depends": [
        "base",
        "web",
        "ipai_workos_core",
        "ipai_workos_blocks",
        "ipai_workos_db",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/search_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
