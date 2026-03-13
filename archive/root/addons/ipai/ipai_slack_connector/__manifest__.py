# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "IPAI Slack Connector",
    "version": "19.0.1.0.0",
    "summary": "Thin outbound Slack webhook adapter for ipai_* modules",
    "description": """
IPAI Slack Connector
====================

Minimal AbstractModel (`ipai.slack.connector`) that other ipai_* modules
inherit to post messages to a Slack Incoming Webhook.

Configuration (env vars — NOT committed to git):
  SLACK_WEBHOOK_URL — Slack Incoming Webhook URL
                      e.g. https://hooks.slack.com/services/T.../B.../xxx

If SLACK_WEBHOOK_URL is absent, _ipai_slack_enabled() returns False and
calling _ipai_post_message() raises UserError (safe for local dev when
env var is simply not set — callers should guard with _ipai_slack_enabled()).

See: docs/ai/INTEGRATIONS.md (Slack section)
    """,
    "category": "Tools",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "depends": ["base"],
    "data": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
