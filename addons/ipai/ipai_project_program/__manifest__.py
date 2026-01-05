# -*- coding: utf-8 -*-
{
    "name": "IPAI Project Program (Program + IM Projects)",
    "summary": "Program (parent project) + Implementation Modules (IM1/IM2) as child projects + Directory + seed loader",
    "description": """
Project Program & Implementation Modules
========================================

This module provides a hierarchical project structure for managing complex
programs with multiple Implementation Modules (IMs).

Key Features:
- Program projects as parent containers
- Implementation Modules (IM1, IM2, ...) as child projects
- Finance Directory for role-based task assignment
- Idempotent JSON seed loader
- Convert legacy phases to IM projects wizard
- Roll-up counts and reporting at program level

Structure:
----------
Program (PRJ-2025-002)
  ├── IM1 - Month-End Closing Planning
  └── IM2 - Tax Filing & Compliance
    """,
    "version": "18.0.1.0.0",
    "category": "Project",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_project_program",
    "license": "LGPL-3",
    "depends": ["project", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/project_project_views.xml",
        "views/directory_views.xml",
        "views/menus.xml",
        "wizard/convert_phases_wizard_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
