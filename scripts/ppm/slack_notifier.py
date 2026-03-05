# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Slack notification client for PPM Clarity events.

Reuses the Pulser/ipai_slack_connector webhook pattern (PR #441).
Posts structured messages to dedicated PPM Clarity channels.

Channels:
  - #ppm-clarity-logs: Sync success, daily reconciliation reports
  - #ppm-clarity-alerts: Sync failures, retry notifications
  - #ppm-clarity-conflicts: Conflict escalation with interactive buttons
"""

import json
import logging
import os

import requests

_logger = logging.getLogger(__name__)


# Channel configuration (override via environment)
DEFAULT_CHANNELS = {
    "logs": os.environ.get("SLACK_CHANNEL_LOGS", "#ppm-clarity-logs"),
    "alerts": os.environ.get("SLACK_CHANNEL_ALERTS", "#ppm-clarity-alerts"),
    "conflicts": os.environ.get("SLACK_CHANNEL_CONFLICTS", "#ppm-clarity-conflicts"),
}


class SlackNotifier:
    """Posts PPM Clarity notifications to Slack via Incoming Webhooks.

    Uses the same webhook pattern as ipai_slack_connector.utils.slack_client.
    """

    def __init__(self, webhook_url=None, channels=None):
        """Initialize notifier.

        Args:
            webhook_url: Slack Incoming Webhook URL. Falls back to SLACK_WEBHOOK_URL env.
            channels: Dict mapping role → channel name. Falls back to DEFAULT_CHANNELS.
        """
        self.webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL", "")
        self.channels = channels or DEFAULT_CHANNELS

    def _post(self, channel, text, blocks=None):
        """Post a message to Slack via webhook.

        Args:
            channel: Channel name (e.g., "#ppm-clarity-logs").
            text: Fallback text (shown in notifications).
            blocks: Optional Block Kit blocks for rich formatting.
        """
        if not self.webhook_url:
            _logger.warning("SLACK_WEBHOOK_URL not configured; skipping notification")
            return None

        payload = {"channel": channel, "text": text}
        if blocks:
            payload["blocks"] = blocks

        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            if resp.status_code >= 300:
                _logger.error("Slack webhook HTTP %s: %s", resp.status_code, resp.text[:200])
            return resp
        except requests.RequestException as exc:
            _logger.error("Slack webhook error: %s", exc)
            return None

    # ── Notification methods ──────────────────────────────────────────

    def notify_sync_success(self, event_data):
        """Post sync success to #ppm-clarity-logs.

        Args:
            event_data: Dict with plane_issue_id, odoo_task_id, title,
                       event_type, fields_synced, duration_ms.
        """
        text = (
            "Sync completed: Plane issue #%s \"%s\" -> Odoo task #%s\n"
            "- Event: %s\n"
            "- Fields: %s\n"
            "- Duration: %.1fs"
        ) % (
            event_data.get("plane_issue_id", "?"),
            event_data.get("title", "Untitled"),
            event_data.get("odoo_task_id", "?"),
            event_data.get("event_type", "unknown"),
            ", ".join(event_data.get("fields_synced", [])),
            event_data.get("duration_ms", 0) / 1000,
        )

        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": ":white_check_mark: " + text},
            }
        ]

        self._post(self.channels["logs"], text, blocks)

    def notify_sync_failure(self, event_data):
        """Post sync failure to #ppm-clarity-alerts.

        Args:
            event_data: Dict with plane_issue_id, error_message,
                       retry_count, event_id.
        """
        text = (
            "Sync failed: Plane issue #%s\n"
            "- Error: %s\n"
            "- Retry: %s/3\n"
            "- Manual: `/ppm-retry %s`"
        ) % (
            event_data.get("plane_issue_id", "?"),
            event_data.get("error_message", "Unknown error"),
            event_data.get("retry_count", 0),
            event_data.get("event_id", "?"),
        )

        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": ":warning: " + text},
            }
        ]

        self._post(self.channels["alerts"], text, blocks)

    def notify_conflict(self, conflict_data):
        """Post conflict to #ppm-clarity-conflicts with resolution options.

        Args:
            conflict_data: Dict with title, field_name, plane_value,
                          odoo_value, link_id, last_sync_hours.
        """
        text = (
            "Conflict detected: Both systems modified same field\n"
            "- Item: \"%s\"\n"
            "- Field: %s\n"
            "- Plane: \"%s\"\n"
            "- Odoo: \"%s\"\n"
            "- Last sync: %s hours ago"
        ) % (
            conflict_data.get("title", "Unknown"),
            conflict_data.get("field_name", "unknown"),
            conflict_data.get("plane_value", ""),
            conflict_data.get("odoo_value", ""),
            conflict_data.get("last_sync_hours", "?"),
        )

        link_id = conflict_data.get("link_id", "?")

        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": ":rotating_light: " + text},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Use Plane"},
                        "style": "primary",
                        "action_id": "ppm_resolve_plane",
                        "value": "plane_%s" % link_id,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Use Odoo"},
                        "action_id": "ppm_resolve_odoo",
                        "value": "odoo_%s" % link_id,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Manual Merge"},
                        "style": "danger",
                        "action_id": "ppm_resolve_manual",
                        "value": "manual_%s" % link_id,
                    },
                ],
            },
        ]

        self._post(self.channels["conflicts"], text, blocks)

    def notify_reconciliation_report(self, report_data):
        """Post daily reconciliation summary to #ppm-clarity-logs.

        Args:
            report_data: Dict with items_scanned, conflicts_resolved,
                        errors, duration_ms.
        """
        text = (
            "Nightly reconciliation complete (2 AM UTC+08:00)\n"
            "- Items scanned: %s\n"
            "- Conflicts resolved: %s\n"
            "- Errors: %s\n"
            "- Duration: %.1fs"
        ) % (
            report_data.get("items_scanned", 0),
            report_data.get("conflicts_resolved", 0),
            report_data.get("errors", 0),
            report_data.get("duration_ms", 0) / 1000,
        )

        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": ":bar_chart: " + text},
            }
        ]

        self._post(self.channels["logs"], text, blocks)
