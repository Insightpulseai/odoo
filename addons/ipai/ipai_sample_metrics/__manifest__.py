# -*- coding: utf-8 -*-
# Copyright 2026 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
{
    "name": "IPAI Sample Metrics",
    "summary": "Minimal OCA-style example app: metrics with list/form views and API helpers",
    "version": "18.0.1.0.0",
    "category": "Reporting",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/sample_metric_views.xml",
        "data/sample_metric_data.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
