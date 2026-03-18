# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Core",
    "version": "19.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "Core AI provider, conversation, and tool registry models",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/ai_provider_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
