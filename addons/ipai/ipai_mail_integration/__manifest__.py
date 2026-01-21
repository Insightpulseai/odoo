# -*- coding: utf-8 -*-
{
    "name": "IPAI Mail Integration",
    "summary": "Direct mail integration with Gmail/Outlook OAuth (EE mail_plugin replacement)",
    "description": """
IPAI Mail Integration
=====================

This module provides direct integration with Gmail and Outlook 365
without requiring Odoo Enterprise mail_plugin modules.

Features:
- OAuth configuration for Google and Microsoft
- Direct API integration via MS Graph and Gmail API
- Mail tracking and sync capabilities
- No IAP or EE dependencies

Replaces:
- mail_plugin (EE)
- mail_plugin_gmail (EE)
- mail_plugin_outlook (EE)
    """,
    "version": "18.0.1.0.0",
    "category": "InsightPulse/Communication",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        # CE core only - NO EE dependencies
        "base",
        "mail",
        "auth_oauth",
        "fetchmail",
        # OCA (if available)
        # "mail_tracking",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/mail_oauth_provider_views.xml",
        "views/res_config_settings_views.xml",
        "data/config_parameters.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
