{
    "name": "IPAI Workload Center",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "summary": (
        "Operational control surface for workload "
        "lifecycle, validation, and evidence"
    ),
    "description": """
        Workload Center for InsightPulse AI platform operators.

        Provides:
        - Workload registration and topology management
        - Environment inventory (dev/staging/prod)
        - Release tracking with deployment evidence
        - Validation run records
        - Evidence artifact capture

        Design: Odoo is a source/action surface. The cross-business
        analytical model lives in Databricks. The org-wide control
        plane lives in platform/.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/workload_actions.xml",
        "views/workload_views.xml",
        "views/workload_menu.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "development_status": "Alpha",
}
