# -*- coding: utf-8 -*-
{
    "name": "InsightPulse Dev Studio Base",
    "summary": "Base OCA/CE module bundle and dev tools for InsightPulse",
    "version": "18.0.1.1.0",
    "category": "Tools",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
        "mail",
        "contacts",
        # "board",  # TODO: Verify availability in Odoo 18 CE
        # "base_automation",  # TODO: Add when base_automation is confirmed in addons_path
        "project",
        # "documents",  # Enterprise-only - use OCA dms when available
    ],
    "data": [],
    "installable": True,
    "application": False,
}
