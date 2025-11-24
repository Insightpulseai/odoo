# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance PPM",
    "summary": "Finance Project Portfolio Management (Notion Parity).",
    "version": "18.0.1.1.1",
    "category": "Accounting/Finance",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "project",
        "board",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/finance_project_data.xml",
        "data/finance_person_directory.xml",
        "views/finance_person_views.xml",
        "views/finance_task_extensions.xml",
        "views/bir_schedule_views.xml",
        "views/ppm_dashboard_views.xml",
        "views/menus.xml",
        "data/bir_schedule_seed.xml",
    ],
    "installable": True,
    "application": True,
}
