# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance Close Seed",
    "summary": "Seed data for Month-End Close + BIR Tax Filing + PH Holidays",
    "description": """
Finance Close Seed Data
=======================

This module seeds:
- 3 Projects (BIR Tax Filing, Month-End Close Template, Month-end closing)
- Task Categories as project.tags
- 36 Month-End Close template tasks
- 29 BIR Tax Filing tasks with deadlines
- PH Holidays for 2026 (bound to standard calendar)

Generated from: Month-end Closing Task and Tax Filing.xlsx
    """,
    "version": "18.0.1.0.0",
    "category": "Accounting/Project",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["project", "resource"],
    "data": [
        "data/ir_config_parameter.xml",
        "data/projects.xml",
        "data/tags.xml",
        "data/holidays.xml",
        "data/tasks_month_end.xml",
        "data/tasks_bir.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
