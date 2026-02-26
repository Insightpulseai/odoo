# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "IPAI Mailgun SMTP Transport",
    "version": "19.0.1.0.0",
    "summary": "Mailgun SMTP outbound server for mg.insightpulseai.com (port 2525, bypasses DO block)",
    "description": """
IPAI Mailgun SMTP Transport
=============================

Registers an Odoo outgoing mail server that sends via Mailgun SMTP on port 2525.

Port 2525 is Mailgun's alternate submission port and is not blocked on DigitalOcean
droplets (unlike ports 25/587/465 which may be blocked).

Configuration:
  SMTP server : smtp.mailgun.org
  Port        : 2525 (STARTTLS)
  Username    : no-reply@mg.insightpulseai.com
  Password    : set via scripts/setup_mailgun_smtp_password.sh (never commit)
  From        : no-reply@mg.insightpulseai.com
  Reply-To    : support@insightpulseai.com (optional — Zoho inbound)

DNS auth records for mg.insightpulseai.com:
  infra/dns/mailgun_mg_insightpulseai_com.yaml

Sending domain: mg.insightpulseai.com (outbound-only, Zoho handles inbound).
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
