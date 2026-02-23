# -*- coding: utf-8 -*-
{
    "name": "IPAI Mailgun Bridge",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "Mailgun <-> Odoo integration for outbound + inbound + tracking",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "crm",
        "project",
    ],
    "data": [
        "data/mailgun_parameters.xml",
        "data/mailgun_catchall_aliases.xml",
    ],
    "application": False,
    "installable": True,
}
