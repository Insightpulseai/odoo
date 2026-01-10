{
    "name": "IPAI Command Center",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "Platform cockpit for runs, KPIs, alerts, and AI",
    "description": """
IPAI Command Center
===================

Unified platform cockpit that combines:
- Run timeline (queue_job states)
- KPI tiles (from kpi_dashboard / MIS outputs)
- "Ask AI" entrypoint
- Audit & errors panel

This is the central hub for monitoring and controlling
all IPAI platform operations.

Features:
---------
* Real-time run monitoring
* KPI dashboard integration
* AI query interface
* Error tracking and alerts
* Audit log viewer
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_design_system_apps_sdk",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/command_center_views.xml",
        "views/command_center_run_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_command_center/static/src/scss/command_center.scss",
            "ipai_command_center/static/src/js/command_center_dashboard.js",
            "ipai_command_center/static/src/xml/command_center_templates.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
}
