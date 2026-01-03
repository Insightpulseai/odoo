# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance Close Automation",
    "summary": "Month-end close generator with working-day deadline offsets",
    "description": """
Finance Close Automation
========================

This module provides:
- Wizard to generate monthly closing projects from template
- Monthly cron to auto-generate
- Per-task deadline offset field (workdays before month-end)
- Working-day computation respecting PH holidays
- Category-based and task-specific offset rules via CSV

Features:
---------
- Clone 'Month-End Close Template' -> 'Month-end closing YYYY-MM'
- Compute deadlines using ipai_deadline_offset_workdays field
- Respect resource.calendar.leaves (PH holidays)
- Deterministic offset rules (priority, exact/contains/regex/category)

Usage:
------
1. Edit data/deadline_offset_rules.csv to set offsets
2. Use wizard: Project > Finance Close > Generate Month-End Close
3. Or let monthly cron auto-generate
    """,
    "version": "18.0.1.0.0",
    "category": "Accounting/Project",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["project", "resource", "ipai_finance_close_seed"],
    "data": [
        "security/ir.model.access.csv",
        "views/close_wizard_views.xml",
        "data/cron.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
