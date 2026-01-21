# -*- coding: utf-8 -*-
# Copyright (C) InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).
{
    "name": "IPAI Vertical Media (CES)",
    "version": "18.0.1.0.0",
    "summary": "Creative/media vertical layer for CES on top of Odoo 18 CE + OCA.",
    "description": """
IPAI Vertical Media (CES)
=========================

Creative/media vertical layer providing:
- Campaign management integration with CRM and Projects
- Media mix tracking (TV, OOH, Digital, Print, Radio)
- Budget bucket classification (Production, Media, Agency Fees)
- TBWA flagship campaign tagging
- Client and brand hierarchies for LIONS/CES reporting
- Integration with Project timesheets

This module is part of the CES creative analytics platform.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Verticals/Services",
    "license": "AGPL-3",
    "depends": [
        "crm",
        "sale_management",
        "project",
        "hr_timesheet",
        "account",
        "ipai_workspace_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/media_campaign_stages.xml",
        "data/media_project_templates.xml",
        "data/media_budget_categories.xml",
        "views/project_project_views.xml",
        "views/sale_order_views.xml",
        "views/crm_lead_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
