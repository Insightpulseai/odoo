# -*- coding: utf-8 -*-
{
    "name": "IPAI Mail Integration",
    "version": "18.0.1.0.0",
    "category": "InsightPulse/Communication",
    "summary": "Mailgun/SMTP/OAuth mail integration without IAP dependencies",
    "description": """
IPAI Mail Integration
=====================

Direct email integration for IPAI CE+OCA stack without IAP dependencies.

Features:
- Direct SMTP gateway integration
- Mailgun API support
- OAuth2 authentication for SMTP
- Email tracking and analytics
- Template management
- Bounce handling

This module replaces IAP-based mail services with direct integrations.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_enterprise_bridge",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/mail_integration_data.xml",
        "views/mail_integration_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
