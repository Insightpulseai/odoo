# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance BIR Compliance (Schedule + Generator)",
    "summary": "JSON-seeded BIR schedule that generates Prep/Review/Approval/Filing tasks into IM2",
    "description": """
BIR Compliance Task Generator
=============================

This module provides schedule-driven task generation for BIR (Bureau of
Internal Revenue) tax filing compliance workflows.

Key Features:
- JSON-seeded BIR schedule items
- Prep/Review/Approval/Filing task sequences
- Business day deadline computation
- Role-based assignment via Directory codes
- Idempotent generation (safe to re-run)

BIR Forms Supported:
--------------------
- 1601-C (Monthly Withholding Tax)
- 0619-E (Expanded Withholding Tax)
- 2550M (Monthly VAT)
- 2550Q (Quarterly VAT)
- 1702Q (Quarterly Income Tax)
- And more...

Usage:
------
1. Configure schedule via seed JSON or UI
2. Run generator wizard with date range
3. Tasks are created in IM2 project
    """,
    "version": "18.0.1.0.0",
    "category": "Accounting/Project",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["project", "mail", "ipai_project_program"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/bir_schedule_views.xml",
        "views/menus.xml",
        "wizard/generate_bir_tasks_wizard_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
