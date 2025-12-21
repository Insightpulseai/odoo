{
    "name": "IPAI Close Task Orchestration",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Month-end close task orchestration with 3-stage approval workflow (Prep → Review → Approve)",
    "description": """
        Enterprise month-end close task management:
        - 21 task categories from TBWA close process
        - 3-stage workflow: Preparation → Review → Approval
        - Department routing: RIM, JPAL, BOM, CKVC, FD
        - Timeline enforcement: 5-6 day close cycle
        - Exception tracking with escalation
        - GL integration for accruals and postings

        Based on SAP AFC (Advanced Financial Closing) patterns.
    """,
    "depends": ["base", "mail", "account", "ipai_tbwa_finance"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/close_task_categories.xml",
        "data/close_task_templates.xml",
        "data/ir_cron.xml",
        "views/close_cycle_views.xml",
        "views/close_task_views.xml",
        "views/close_exception_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
