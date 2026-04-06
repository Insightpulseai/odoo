{
    "name": "IPAI Finance Close",
    "version": "18.0.1.0.0",
    "summary": "Closing task orchestration: templates, task lists, dependencies, and compliance tracking",
    "description": """
IPAI Finance Close — Period-End Closing Orchestration
======================================================

Closing task management inspired by SAP Advanced Financial Closing:

* **Templates** define reusable closing checklists (month-end, BIR, year-end)
* **Template lines** define individual tasks with type, role assignments,
  relative deadlines, and dependencies
* **Task lists** instantiate a template for a specific period (e.g., March 2026)
* **Tasks** track execution with processor/responsible assignment,
  status cascade, evidence attachments, and audit trail

Status cascade (SAP Tax Compliance-inspired):
  All tasks completed → task list auto-closes → overdue alerts suppressed

Stage model:
  - Month-End: Preparation → Review → Approval
  - BIR: Preparation → Report Approval → Payment Approval → Filing & Payment

BIR deadline reference data included for PH compliance.
    """,
    "category": "Accounting",
    "license": "LGPL-3",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "depends": [
        "account",
        "project",
        "mail",
        "hr",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/closing_template_views.xml",
        "views/closing_task_list_views.xml",
        "views/closing_task_views.xml",
        "views/menus.xml",
        "data/bir_deadline_reference.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
