# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Tests for Slack notification client."""

import unittest
from unittest.mock import MagicMock, patch

from scripts.ppm.slack_notifier import SlackNotifier


class TestSlackNotifier(unittest.TestCase):
    """Test Slack notification formatting and delivery."""

    def setUp(self):
        self.notifier = SlackNotifier(
            webhook_url="https://hooks.slack.com/test",
            channels={
                "logs": "#test-logs",
                "alerts": "#test-alerts",
                "conflicts": "#test-conflicts",
            },
        )

    @patch("scripts.ppm.slack_notifier.requests")
    def test_sync_success_posts_to_logs(self, mock_requests):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_requests.post.return_value = mock_resp

        self.notifier.notify_sync_success({
            "plane_issue_id": "issue-123",
            "title": "Feature X",
            "odoo_task_id": 456,
            "event_type": "plane_to_odoo",
            "fields_synced": ["title", "description"],
            "duration_ms": 1200,
        })

        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        payload = call_args[1]["json"] if "json" in call_args[1] else call_args[0][1]
        self.assertEqual(payload["channel"], "#test-logs")

    @patch("scripts.ppm.slack_notifier.requests")
    def test_sync_failure_posts_to_alerts(self, mock_requests):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_requests.post.return_value = mock_resp

        self.notifier.notify_sync_failure({
            "plane_issue_id": "issue-789",
            "error_message": "Connection timeout",
            "retry_count": 2,
            "event_id": "evt-001",
        })

        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        payload = call_args[1]["json"] if "json" in call_args[1] else call_args[0][1]
        self.assertEqual(payload["channel"], "#test-alerts")

    @patch("scripts.ppm.slack_notifier.requests")
    def test_conflict_posts_with_buttons(self, mock_requests):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_requests.post.return_value = mock_resp

        self.notifier.notify_conflict({
            "title": "Sprint Planning",
            "field_name": "title",
            "plane_value": "Sprint Q1",
            "odoo_value": "Sprint Session",
            "link_id": "link-001",
            "last_sync_hours": 2,
        })

        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        payload = call_args[1]["json"] if "json" in call_args[1] else call_args[0][1]
        self.assertEqual(payload["channel"], "#test-conflicts")
        # Should have blocks with action buttons
        self.assertIn("blocks", payload)
        action_block = [b for b in payload["blocks"] if b["type"] == "actions"]
        self.assertEqual(len(action_block), 1)
        self.assertEqual(len(action_block[0]["elements"]), 3)

    @patch("scripts.ppm.slack_notifier.requests")
    def test_reconciliation_report(self, mock_requests):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_requests.post.return_value = mock_resp

        self.notifier.notify_reconciliation_report({
            "items_scanned": 1234,
            "conflicts_resolved": 3,
            "errors": 0,
            "duration_ms": 45000,
        })

        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        payload = call_args[1]["json"] if "json" in call_args[1] else call_args[0][1]
        self.assertIn("1234", payload["text"])

    def test_no_webhook_skips_silently(self):
        """When SLACK_WEBHOOK_URL is empty, notifications are skipped."""
        notifier = SlackNotifier(webhook_url="")
        # Should not raise
        result = notifier.notify_sync_success({"plane_issue_id": "x", "title": "t",
                                                "odoo_task_id": 1, "event_type": "test",
                                                "fields_synced": [], "duration_ms": 0})
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
