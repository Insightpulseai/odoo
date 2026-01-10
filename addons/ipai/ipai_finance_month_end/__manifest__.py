# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance Month-End (Templates + Generator)",
    "summary": "JSON-seeded month-end templates that generate Preparation/Review/Approval tasks into IM1",
    "description": """
Month-End Task Generator
========================

This module provides template-driven task generation for recurring month-end
closing workflows.

Key Features:
- JSON-seeded month-end templates
- Preparation/Review/Approval task triplets
- Role-based assignment via Directory codes
- Business day deadline computation
- Idempotent generation (safe to re-run)

Templates:
----------
- Payroll & Personnel
- Accruals & Amortization
- WIP Reconciliation
- Trial Balance
- And more...

Usage:
------
1. Configure templates via seed JSON or UI
2. Run generator wizard with anchor date
3. Tasks are created in IM1 project
    """,
    "version": "18.0.1.0.0",
    "category": "Accounting/Project",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_finance_month_end",
    "license": "LGPL-3",
    "depends": ["project", "mail", "ipai_project_program"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/month_end_template_views.xml",
        "views/menus.xml",
        "wizard/generate_month_end_wizard_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
