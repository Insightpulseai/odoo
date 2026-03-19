# -*- coding: utf-8 -*-
{
    "name": "IPAI Agent Skills",
    "version": "19.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "Declarative agent skill registry for Odoo consultation, "
    "app development, web development, and UI/UX design workflows",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/skill_definition_views.xml",
        "views/skill_execution_views.xml",
        "data/skill_categories.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
