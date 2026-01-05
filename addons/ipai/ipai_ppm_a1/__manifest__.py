# -*- coding: utf-8 -*-
{
    "name": "IPAI PPM A1 Control Center",
    "version": "18.0.1.0.0",
    "category": "Project/Portfolio",
    "summary": "A1 Control Center - Workstreams, Templates, Tasks, Checks + Seed Import/Export",
    "description": """
IPAI PPM A1 Control Center
==========================

A1 Control Center for managing:
- Workstreams (organizational units)
- Task Templates (reusable task definitions)
- Tasks (period-specific instances)
- Checks/Scenarios (STC validation rules)
- Seed Import/Export (YAML-based configuration)

This module provides the "A1" layer that can instantiate into
close cycles via the ipai_close_orchestration module.

Key Features:
- Role-based workstream assignment (RIM, JPAL, BOM, CKVC, etc.)
- Hierarchical template structure (phase → workstream → template → steps)
- Idempotent seed import with external key mapping
- Webhook support for n8n integration
- Multi-company aware with record rules
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_ppm_a1",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "project",
    ],
    "data": [
        "security/a1_security.xml",
        "security/ir.model.access.csv",
        "data/a1_role_data.xml",
        "views/a1_workstream_views.xml",
        "views/a1_template_views.xml",
        "views/a1_task_views.xml",
        "views/a1_tasklist_views.xml",
        "views/a1_check_views.xml",
        "views/a1_menu.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": True,
}
