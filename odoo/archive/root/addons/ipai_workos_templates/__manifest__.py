# -*- coding: utf-8 -*-
{
    "name": "IPAI Work OS Templates",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Page and database templates",
    "description": """
        Template module for reusable page/database structures:
        - Page templates with pre-defined blocks
        - Database templates with schema
        - Apply templates to create new pages/databases
        - Template gallery
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
        "ipai_workos_core",
        "ipai_workos_blocks",
        "ipai_workos_db",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/template_views.xml",
        "data/default_templates.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
