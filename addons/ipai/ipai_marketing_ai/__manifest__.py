# -*- coding: utf-8 -*-
{
    "name": "IPAI Marketing AI (Content + Social Hygiene)",
    "version": "18.0.1.0.0",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_marketing_ai",
    "license": "LGPL-3",
    "category": "Marketing",
    "summary": "Umbrella module for AI-powered marketing automation workflows",
    "description": """
IPAI Marketing AI (CE/OCA-first)
================================

Umbrella module that bundles AI-powered marketing automation capabilities
on a CE/OCA foundation.

Features:
---------
* Content generation and optimization workflows
* Social media hygiene and scheduling
* AI-assisted campaign planning
* Integration with Ask AI for marketing insights

Dependencies:
-------------
This module installs the CE/OCA automation backbone plus IPAI AI primitives.
Social/Marketing automation is handled through queue_job for async operations.

CE/OCA First:
-------------
This module follows the CE/OCA-first philosophy:
- queue_job for async operations
- base_automation for trigger-based workflows
- IPAI modules only for differentiating AI features
""",
    "depends": [
        # Core
        "base",
        "mail",
        "mass_mailing",
        # IPAI AI primitives
        "ipai_ask_ai",
        "ipai_agent_core",
    ],
    "data": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
