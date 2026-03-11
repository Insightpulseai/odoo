# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "IPAI Zoho Mail Integration",
    "summary": "Zoho Mail SMTP/IMAP with settings panel, user linking, and fetch wizard",
    "description": """
IPAI Zoho Mail Integration
==========================

This module configures Odoo email settings for production use with Zoho Mail.

Features:
---------
* Outgoing SMTP server (smtppro.zoho.com:587 STARTTLS)
* Incoming IMAP server (imappro.zoho.com:993 SSL)
* System parameters for catchall domain and base URL
* Email aliases for sales, support, accounting
* Per-user Zoho Mail address field
* Settings panel with SMTP/IMAP configuration
* Manual fetch wizard with date filter

Configuration:
--------------
Before installing, ensure these environment variables are set:
* ZOHO_SMTP_PASSWORD - App password for noreply@insightpulseai.com
* ZOHO_IMAP_PASSWORD - App password for catchall@insightpulseai.com

DNS Requirements:
-----------------
* MX records pointing to mx.zoho.com, mx2.zoho.com, mx3.zoho.com
* SPF TXT record: v=spf1 include:zohomail.com ~all
* DKIM TXT record (configured in Zoho admin)
* DMARC TXT record for monitoring

SMTP Delivery Note:
-------------------
Azure does NOT block ports 465/587 — only port 25 is restricted.
E2E verified 2026-03-10: smtppro.zoho.com:587/TLS, sender no-reply@insightpulseai.com.
    """,
    "version": "19.0.1.1.0",
    "category": "Mail",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "mail",
        # "fetchmail" removed — merged into mail in Odoo 19
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/config_params.xml",
        "data/mail_server.xml",
        "data/fetchmail_server.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/zoho_fetch_wizard_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
