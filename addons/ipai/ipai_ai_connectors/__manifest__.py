# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Connectors",
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "Inbound integration hub for AI platform (n8n, GitHub, Slack webhooks)",
    "description": """
IPAI AI Connectors
==================

Provides a secure inbound event intake endpoint for external integrations.

Features:
---------
* Token-authenticated webhook endpoint
* Event persistence with audit trail
* Support for n8n, GitHub, Slack, and custom sources
* Event viewer in admin interface
* Optional event processing hooks

Endpoints:
----------
* POST /ipai_ai_connectors/event - Receive and store integration events

Event Structure:
----------------
{
    "token": "shared_secret",
    "source": "n8n|github|slack|custom",
    "event_type": "issue.created|task.updated|...",
    "ref": "external_id",
    "payload": { ... }
}

Usage:
------
1. Install this module
2. Set IPAI_CONNECTORS_TOKEN environment variable
3. Configure n8n/GitHub/etc to POST to /ipai_ai_connectors/event
4. Monitor events in AI → Integration Events

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/event_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
