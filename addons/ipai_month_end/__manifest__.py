{
    "name": "IPAI Month-End Closing",
    "summary": "SAP AFC replacement - Month-end closing automation",
    "description": """
        Month-end closing automation with SAP Advanced Financial Closing (AFC) feature parity.

        Features:
        - Template-driven task management
        - RACI workflow (Prep → Review → Approve)
        - Holiday-aware workday scheduling (Philippines)
        - Overdue notifications
        - Progress tracking dashboards

        Replaces SAP AFC at zero licensing cost.
    """,
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "IPAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ph_holidays.xml",
        "data/task_templates.xml",
        "data/ir_cron.xml",
        "views/ph_holiday_views.xml",
        "views/task_template_views.xml",
        "views/closing_views.xml",
        "views/task_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
