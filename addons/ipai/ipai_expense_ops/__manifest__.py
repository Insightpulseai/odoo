{
    "name": "IPAI Expense Ops",
    "version": "18.0.1.0.0",
    "summary": "Expense compliance exceptions, multi-step approval, and BIR validation",
    "description": """
IPAI Expense Ops — Expense Compliance & Approval Orchestration
================================================================

SAP Concur-inspired compliance layer for Odoo hr_expense:

* **Exception model**: Structured violation tracking with blocking/non-blocking
  flags, visibility levels, and 3-level attachment (sheet, line, allocation)
* **Extended approval states**: Manager → Budget → Cost Object → External
  Validation → Accounting Review (configurable per company)
* **BIR compliance hook**: External validation step for PH tax compliance

Uses OCA ``base_tier_validation`` if available for approval tier routing.
    """,
    "category": "Human Resources/Expenses",
    "license": "LGPL-3",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "depends": [
        "hr_expense",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/expense_exception_views.xml",
        "views/hr_expense_sheet_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
