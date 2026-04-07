# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "IPAI Workspace Core",
    "version": "18.0.2.0.0",
    "category": "Productivity",
    "summary": "Notion-like collaborative workspace with ERP data integration",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_foundation",
        "ipai_odoo_copilot",  # Foundry gateway (replaces ipai_ai_copilot)
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/workspace_views.xml",
        "views/workspace_page_views.xml",
        "views/workspace_saved_query_views.xml",
        "views/workspace_evidence_pack_views.xml",
        "views/workspace_menus.xml",
        "data/copilot_tools.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
