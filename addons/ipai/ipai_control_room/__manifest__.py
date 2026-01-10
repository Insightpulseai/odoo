# -*- coding: utf-8 -*-
{
    "name": "IPAI Control Room",
    "version": "18.0.1.0.0",
    "category": "Productivity/Operations",
    "summary": "Control Room for pipelines, data quality, and operational insights",
    "description": """
IPAI Control Room
=================

A comprehensive operations control center for managing:

* **Pipelines**: ETL/automation workflows with stages, steps, and runs
* **Data Quality**: Rules, checks, and issue tracking
* **Advisor**: AI-powered recommendations and playbooks
* **Projects**: Integration with project.project for cross-functional work
* **Settings**: Feature flags, connectors, and notifications

Sidebar Navigation:
-------------------
* Overview - Aggregated view of runs, issues, advice, and tasks
* Pipelines - Pipeline management and execution monitoring
* Data Quality - Rule definition and health monitoring
* Advisor - Recommendations and action tracking
* Projects - Native project.project integration
* Settings - System configuration and integrations

Design System:
--------------
Uses Microsoft Fluent 2 design tokens for consistent styling
across Odoo and external applications.

Architecture:
-------------
* control.pipeline - Pipeline definitions with stages/steps
* control.run - Execution instances with event logs
* control.dq.rule - Data quality rule definitions
* control.dq.issue - Issue tracking with SLA support
* control.advice - AI-generated recommendations
* control.connector - External system integrations
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "project",
        "web",
        "ipai_theme_fluent2",
    ],
    "data": [
        # Security
        "security/control_room_security.xml",
        "security/ir.model.access.csv",
        # Data
        "data/control_sequence.xml",
        # Views
        "views/control_pipeline_views.xml",
        "views/control_run_views.xml",
        "views/control_dq_views.xml",
        "views/control_advisor_views.xml",
        "views/control_settings_views.xml",
        "views/control_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_control_room/static/src/scss/control_room.scss",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
