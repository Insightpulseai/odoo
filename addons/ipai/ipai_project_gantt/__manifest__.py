# -*- coding: utf-8 -*-
{
    "name": "IPAI Project Gantt (CE)",
    "version": "18.0.1.0.0",
    "category": "Project",
    "summary": "Community Gantt-like planning view for Project tasks (no Enterprise deps).",
    "description": """
IPAI Project Gantt (CE)
=======================

Provides a Gantt-like planning view for Odoo CE without Enterprise dependencies.

Features:
---------
- Planned Start / Planned End datetime fields on tasks
- Visual timeline bar chart showing task schedules
- Click-to-open task form
- Project/stage filtering
- Auto-scale timeline based on task dates

Usage:
------
1. Set Planned Start and Planned End on your tasks
2. Navigate to Project > Gantt (IPAI) menu
3. Click any task bar to open the task form

Note: This is a CE-safe implementation that does not depend on Enterprise Gantt views.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": ["project", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_task_views.xml",
        "views/gantt_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_project_gantt/static/src/scss/gantt.scss",
            "ipai_project_gantt/static/src/xml/gantt_templates.xml",
            "ipai_project_gantt/static/src/js/gantt_client_action.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
