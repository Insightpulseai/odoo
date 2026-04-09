# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "IPAI Project Timeline Fix",
    "summary": "Strip unsupported timeline view type from project actions",
    "version": "18.0.1.0.0",
    "category": "Project Management",
    "author": "InsightPulseAI",
    "website": "https://github.com/Insightpulseai/odoo",
    "license": "LGPL-3",
    "depends": [
        "project_timeline",
    ],
    "data": [
        "views/fix_timeline_actions.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
}
