# -*- coding: utf-8 -*-
{
    "name": "IPAI Work OS Database",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Notion-style databases with typed properties",
    "description": """
        Database module providing Notion-like structured data:
        - Databases with typed properties (columns)
        - Property types: text, number, select, multi-select, date, checkbox, person
        - Rows as records with inline editing
        - Relations between databases
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
        "ipai_workos_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/database_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_workos_db/static/src/scss/database.scss",
            "ipai_workos_db/static/src/js/row_editor.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
