# -*- coding: utf-8 -*-
{
    "name": "IPAI Portfolio & Program Management",
    "summary": "Portfolio/Program governance layer with risk register, KPI snapshots, and resource allocation",
    "description": """
Portfolio & Program Management (PPM)
====================================

Enterprise-grade portfolio and program management for Odoo 18 CE.

Key Features:
-------------
* **Portfolios** - Strategic grouping of programs with health scoring
* **Programs** - Multi-project containers with budget tracking
* **Risk Register** - Impact/probability matrix with mitigation tracking
* **Resource Allocation** - Capacity planning with overload detection
* **KPI Snapshots** - Time-series metrics from Odoo/Superset/Supabase

Models:
-------
* ppm.portfolio - Strategic portfolio container
* ppm.program - Program linking multiple projects
* ppm.risk - Risk register entries
* ppm.resource.allocation - Resource capacity tracking
* ppm.kpi.snapshot - KPI measurements over time

Architecture:
-------------
Follows "Config → OCA → Delta → New" philosophy.
Integrates with ipai_project_program and ipai_clarity_ppm_parity.

Author: InsightPulse AI
License: LGPL-3
    """,
    "version": "18.0.1.0.0",
    "category": "Project Management",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_ppm",
    "license": "LGPL-3",
    "depends": [
        "project",
        "hr",
        "mail",
    ],
    "data": [
        "security/ppm_security.xml",
        "security/ir.model.access.csv",
        "views/portfolio_views.xml",
        "views/program_views.xml",
        "views/risk_views.xml",
        "views/resource_allocation_views.xml",
        "views/kpi_snapshot_views.xml",
        "views/menus.xml",
        "data/kpi_definitions.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
