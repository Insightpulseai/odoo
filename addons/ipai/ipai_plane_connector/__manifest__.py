# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "IPAI Plane Connector",
    "version": "19.0.1.0.0",
    "summary": "Generic Plane API connector with REST client, webhook verification, and dedup",
    "description": """
IPAI Plane Connector
====================

Generic Plane.so API connector providing:

- **PlaneClient** — pure-Python REST client with rate-limiting, pagination,
  and dual auth (API key / OAuth token).
- **Webhook verification** — HMAC-SHA256 signature checking.
- **Dedup ledger** — ``plane.webhook.delivery`` model prevents reprocessing.
- **AbstractModel** — ``ipai.plane.connector`` that domain modules inherit
  to get a ready-made ``_plane_client()`` and webhook helpers.

Configuration (ir.config_parameter — Settings > Technical > Parameters):
  plane.base_url       — Plane instance URL (default: https://api.plane.so)
  plane.api_key        — API key (required, store in env / secrets)
  plane.workspace_slug — Workspace slug (default: insightpulseai)
  plane.webhook_secret — HMAC secret for inbound webhook verification

Mock boundary for tests:
  patch("odoo.addons.ipai_plane_connector.utils.plane_client.PlaneClient")

See: docs/ai/INTEGRATIONS.md (Plane section)
    """,
    "category": "Tools",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
