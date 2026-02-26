# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "IPAI Zoho Mail API Transport",
    "version": "19.0.1.0.0",
    "summary": "Send Odoo outbound mail via Zoho Mail REST API over HTTPS (no SMTP, bypasses DO block)",
    "description": """
IPAI Zoho Mail API Transport
=============================

Direct Odoo → Zoho Mail API integration over HTTPS (port 443).
Bypasses DigitalOcean's SMTP block (ports 25, 465, 587).

Adds a ``use_zoho_api`` boolean to ``ir.mail_server``.
When a mail server has ``use_zoho_api=True``, outbound email is sent
via ``POST https://mail.zoho.com/api/accounts/{accountId}/messages``
using an OAuth2 access token, refreshed automatically using the stored
refresh token.

No Supabase bridge required — credentials live in ``ir.config_parameter``.

Configuration (ir.config_parameter keys — never commit values to git):
  ipai.zoho.client_id       — OAuth app client ID
  ipai.zoho.client_secret   — OAuth app client secret
  ipai.zoho.refresh_token   — Long-lived refresh token
  ipai.zoho.account_id      — Zoho Mail account ID (numeric)
  ipai.zoho.accounts_base   — (optional) default: https://accounts.zoho.com
  ipai.zoho.mail_base       — (optional) default: https://mail.zoho.com

Use the wiring script to set these without touching git:
  scripts/setup_zoho_mail_api.sh

See: docs/contracts/DNS_EMAIL_CONTRACT.md
    """,
    "category": "Mail",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "depends": ["mail"],
    "data": [
        "data/ir_mail_server.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
