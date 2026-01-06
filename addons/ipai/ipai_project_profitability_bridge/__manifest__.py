# -*- coding: utf-8 -*-
{
    "name": "IPAI Project Profitability Bridge",
    "version": "18.0.1.0.1",
    "category": "Project",
    "summary": "Lightweight profitability KPIs per project using analytic lines (CE-safe).",
    "description": """
IPAI Project Profitability Bridge
=================================

Provides project profitability KPIs for Odoo CE using analytic lines as the
unified cost/revenue ledger.

Features:
---------
- Cost, Revenue, Margin, Margin % per project
- Automatic computation from analytic lines
- Batch recompute action
- Scheduled cron for daily updates
- Works with timesheets, invoicing, and manual entries

Convention:
-----------
- Negative amounts in analytic lines = Cost
- Positive amounts in analytic lines = Revenue

Usage:
------
1. Ensure projects have analytic accounts
2. Post analytic lines (timesheet entries, costs, revenues)
3. Navigate to Project > Profitability (IPAI) menu
4. Click "Recompute All" to refresh KPIs

Note: This is a CE-safe implementation that does not depend on Enterprise features.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": ["project", "analytic", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/profitability_views.xml",
        "views/profitability_menu.xml",
        "views/project_views.xml",
        "data/cron.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
