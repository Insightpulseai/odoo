# -*- coding: utf-8 -*-
{
    "name": "IPAI Project Suite (CE)",
    "version": "18.0.1.0.0",
    "summary": "Toggleable enterprise-like project management features for Odoo CE",
    "description": """
IPAI Project Suite (CE)
=======================

Provides toggleable enterprise-like capabilities for Odoo CE projects:

* **Dependencies**: Task dependencies with types (FS/SS/FF/SF) and lag days
* **Milestones**: Project milestones with target dates and task linking
* **Budgeting**: Project budget headers and lines with computed actuals
* **RACI Roles**: Responsible/Accountable/Consulted/Informed assignments
* **Stage Gates**: Approval gates with required checks before advancing
* **Templates**: Project templates with stages, tasks, and tags

All features are controlled via Settings toggles (ir.config_parameter).
When disabled, feature tabs/menus are hidden with no functional side effects.
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_project_suite",
    "category": "Project",
    "license": "LGPL-3",
    "depends": [
        "project",
        "mail",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/project_views.xml",
        "views/task_views.xml",
        "views/milestone_views.xml",
        "views/dependency_views.xml",
        "views/budget_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
