# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "IPAI Mailgun SMTP Transport",
    "version": "19.0.2.0.0",
    "summary": "Authoritative production outgoing mail server via Mailgun SMTP (port 2525).",
    "description": """
IPAI Mailgun SMTP Transport
=============================

Registers the production outgoing mail server that routes through Mailgun SMTP
on port 2525 (not blocked on DigitalOcean droplets).

This is the AUTHORITATIVE prod mail transport. sequence=5 ensures it is selected
above all other active mail servers. SSOT: ssot/odoo/mail.yaml.

Configuration:
  SMTP server : smtp.mailgun.org
  Port        : 2525 (STARTTLS)
  Username    : no-reply@mg.insightpulseai.com
  Password    : injected at install by post_install_hook from ODOO_MAILGUN_SMTP_PASSWORD env var
  From        : no-reply@mg.insightpulseai.com

Password management:
  - Never commit smtp_pass to XML
  - Set ODOO_MAILGUN_SMTP_PASSWORD before running Odoo in production
  - See: ssot/secrets/registry.yaml#mailgun_smtp_password

DNS auth records for mg.insightpulseai.com:
  infra/dns/subdomain-registry.yaml (mg subdomain)
  PR #445: tracking CNAME + DKIM #2 still pending

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
    "post_install": "hooks.post_install_hook",
    "installable": True,
    "auto_install": False,
    "application": False,
}
