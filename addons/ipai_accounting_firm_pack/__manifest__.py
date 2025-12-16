# -*- coding: utf-8 -*-
{
    "name": "IPAI Accounting Firm Pack",
    "summary": "Accounting Firm industry pack for engagements, compliance, and workpapers.",
    "version": "18.0.1.0.0",
    "category": "Accounting/Services",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "account",
        "project",
        "hr_timesheet",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/engagement_views.xml",
        "views/compliance_views.xml",
        "views/workpaper_views.xml",
        "views/menus.xml",
        "data/engagement_data.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
