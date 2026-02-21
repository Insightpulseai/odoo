# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "IPAI Zoho Mail HTTPS Bridge",
    "version": "19.0.1.0.0",
    "summary": "Send Odoo outbound mail via Zoho Mail API over HTTPS (no SMTP, bypasses DO block)",
    "description": """
IPAI Zoho Mail HTTPS Bridge
============================

Overrides mail.mail.send() to POST email payloads to the zoho-mail-bridge
Supabase Edge Function over HTTPS, bypassing DigitalOcean's SMTP block
(ports 25, 465, 587 are blocked on all DO droplets by default).

The existing zoho-mail-bridge edge function handles Zoho OAuth2 token refresh
and sends via Zoho Mail REST API — entirely over HTTPS.

Configuration (Docker / systemd env vars — NOT committed to git):
  ZOHO_MAIL_BRIDGE_URL    — Supabase Edge Function URL
                            e.g. https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/zoho-mail-bridge
  ZOHO_MAIL_BRIDGE_SECRET — Dedicated 32+ char random shared secret.
                            NOT the Supabase anon key (that is a public client credential).
                            Generate with: openssl rand -hex 32
                            Must match BRIDGE_SHARED_SECRET in Supabase Vault.

If these env vars are absent, falls back to standard Odoo SMTP (safe for local dev).
    """,
    "category": "Mail",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "depends": ["mail"],
    "data": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
