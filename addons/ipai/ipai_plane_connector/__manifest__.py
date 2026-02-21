{
    "name": "IPAI Plane Connector",
    "summary": "Bidirectional sync between Odoo projects/tasks and Plane work items",
    "version": "19.0.1.0.0",
    "category": "Project",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "project",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "views/project_task_views.xml",
        "views/plane_sync_log_views.xml",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
}
