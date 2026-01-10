# -*- coding: utf-8 -*-
{
    "name": "IPAI Ops Advisor",
    "summary": "Azure Advisor-style recommendations engine for operational governance",
    "description": """
Ops Advisor - Azure Advisor Clone
=================================

Enterprise-grade operational recommendations engine for Odoo 18 CE.
Mirrors Azure Advisor's 5-category scoring and recommendations pattern.

Categories:
-----------
* **Cost** - Budget optimization, unused resources, efficiency
* **Security** - Access controls, RLS gaps, credential hygiene
* **Reliability** - Availability, backups, redundancy
* **Operational Excellence** - Runbooks, alerts, automation coverage
* **Performance** - Response times, query optimization, capacity

Features:
---------
* Recommendation management with severity levels
* Automated scoring per category (0-100)
* Playbook linking for remediation steps
* External integration via webhooks (n8n collectors)
* CSV/PDF export
* Mattermost notification support
* Superset workbook linking

Architecture:
-------------
- Odoo UI for viewing/managing recommendations
- n8n workflows for signal collection
- Supabase for heavy analytics (optional)
- Edge functions for score computation

Author: InsightPulse AI
License: LGPL-3
    """,
    "version": "18.0.1.0.0",
    "category": "Operations",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_advisor",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/advisor_security.xml",
        "security/ir.model.access.csv",
        "data/advisor_categories.xml",
        "views/category_views.xml",
        "views/recommendation_views.xml",
        "views/playbook_views.xml",
        "views/score_views.xml",
        "views/dashboard_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,  # Supporting module, not a main install target
    "auto_install": False,
}
