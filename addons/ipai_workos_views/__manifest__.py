# -*- coding: utf-8 -*-
{
    "name": "IPAI Work OS Views",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Table, Kanban, and Calendar views for databases",
    "description": """
        Database view module providing Notion-like view options:
        - Table (grid) view with sorting/filtering
        - Kanban view with group-by
        - Calendar view for date properties
        - Saved views (per user and shared)
        - View switcher UI
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "AGPL-3",
    "icon": "fa-th-list",
    "depends": [
        "base",
        "web",
        "ipai_workos_core",
        "ipai_workos_db",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/view_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_workos_views/static/src/scss/views.scss",
            "ipai_workos_views/static/src/js/view_switcher.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
