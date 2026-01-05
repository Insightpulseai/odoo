# -*- coding: utf-8 -*-
{
    "name": "IPAI Close Cycle Orchestration",
    "version": "18.0.1.0.0",
    "category": "Accounting/Close",
    "summary": "Close Cycle Orchestration - Cycles, Tasks, Templates, Checklists, Exceptions, Gates",
    "description": """
IPAI Close Cycle Orchestration
==============================

Execution engine for month-end close and periodic closing processes.

Key Components:
- Close Cycles: Period-based closing runs
- Close Tasks: Individual close items with workflow
- Templates: Reusable task definitions
- Categories: Organizational groupings
- Checklists: Verification items
- Exceptions: Issue tracking and escalation
- Approval Gates: Control checkpoints

Workflow:
- prep → review → approval → done

Automation:
- Cron for due date reminders
- Cron for exception auto-escalation
- Cron for gate status checks
- Webhook events for n8n integration

Bridged from A1 Control Center (ipai_ppm_a1) for seamless
configuration-to-execution flow.
    """,
    "author": "IPAI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "project",
    ],
    "data": [
        "security/close_security.xml",
        "security/ir.model.access.csv",
        "data/close_cron.xml",
        "views/close_cycle_views.xml",
        "views/close_task_views.xml",
        "views/close_template_views.xml",
        "views/close_exception_views.xml",
        "views/close_gate_views.xml",
        "views/close_menu.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": True,
}
