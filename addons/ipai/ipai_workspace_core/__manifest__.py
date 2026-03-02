# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "IPAI Workspace Core",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "summary": "Notion-like collaborative workspace with ERP data integration",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_foundation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/workspace_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
