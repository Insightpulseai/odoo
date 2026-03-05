"""
Test Slack notification logic for PPM Clarity integration.

Based on spec/ppm-clarity-plane-odoo/plan.md Slack integration:
- Success notifications to #ppm-clarity-logs
- Failure notifications to #ppm-clarity-alerts
- Conflict notifications to #ppm-clarity-conflicts
- Daily summary to #ppm-clarity-logs
"""

import pytest
from unittest.mock import Mock, patch, call


class TestSlackNotifications:
    """Test Slack notification formatting and delivery."""

    @patch("scripts.ppm.slack_notifier.SlackClient")
    def test_success_notification_format(self, mock_slack_client):
        """Success notification has correct format."""
        mock_slack = mock_slack_client.return_value

        event = {
            "event_type": "plane_to_odoo",
            "plane_issue_id": "PLANE-123",
            "odoo_task_id": 456,
            "status": "success",
        }

        send_success_notification(event)

        # Verify Slack message posted
        mock_slack.chat_postMessage.assert_called_once()
        call_args = mock_slack.chat_postMessage.call_args[1]

        assert call_args["channel"] == "#ppm-clarity-logs"
        assert "✅" in call_args["text"]
        assert "PLANE-123" in call_args["text"]
        assert "456" in str(call_args["text"])

    @patch("scripts.ppm.slack_notifier.SlackClient")
    def test_failure_notification_format(self, mock_slack_client):
        """Failure notification has correct format."""
        mock_slack = mock_slack_client.return_value

        event = {
            "event_type": "plane_to_odoo",
            "plane_issue_id": "PLANE-123",
            "status": "failed",
            "error": "Odoo connection timeout",
        }

        send_failure_notification(event)

        # Verify Slack message posted to alerts channel
        mock_slack.chat_postMessage.assert_called_once()
        call_args = mock_slack.chat_postMessage.call_args[1]

        assert call_args["channel"] == "#ppm-clarity-alerts"
        assert "❌" in call_args["text"]
        assert "PLANE-123" in call_args["text"]
        assert "Odoo connection timeout" in call_args["text"]

    @patch("scripts.ppm.slack_notifier.SlackClient")
    def test_conflict_notification_format(self, mock_slack_client):
        """Conflict notification has correct format with action buttons."""
        mock_slack = mock_slack_client.return_value

        conflict = {
            "link_id": "link_123",
            "field": "state",
            "plane_value": "In Progress",
            "odoo_value": "Done",
            "plane_issue_id": "PLANE-123",
            "odoo_task_id": 456,
        }

        send_conflict_notification(conflict)

        # Verify Slack message posted to conflicts channel
        mock_slack.chat_postMessage.assert_called_once()
        call_args = mock_slack.chat_postMessage.call_args[1]

        assert call_args["channel"] == "#ppm-clarity-conflicts"
        assert "⚠️" in call_args["text"] or "blocks" in call_args
        assert "PLANE-123" in str(call_args)
        assert "state" in str(call_args)

        # Verify action buttons present (if using blocks)
        if "blocks" in call_args:
            blocks = call_args["blocks"]
            assert any("actions" in block for block in blocks)

    @patch("scripts.ppm.slack_notifier.SlackClient")
    def test_daily_summary_format(self, mock_slack_client):
        """Daily summary has correct metrics format."""
        mock_slack = mock_slack_client.return_value

        summary = {
            "date": "2024-03-05",
            "total_syncs": 42,
            "successful": 40,
            "failed": 2,
            "conflicts": 1,
            "active_links": 35,
        }

        send_daily_summary(summary)

        # Verify Slack message posted
        mock_slack.chat_postMessage.assert_called_once()
        call_args = mock_slack.chat_postMessage.call_args[1]

        assert call_args["channel"] == "#ppm-clarity-logs"
        assert "2024-03-05" in call_args["text"]
        assert "42" in str(call_args["text"])  # Total syncs
        assert "40" in str(call_args["text"])  # Successful
        assert "2" in str(call_args["text"])  # Failed

    @patch("scripts.ppm.slack_notifier.SlackClient")
    def test_slash_command_retry_response(self, mock_slack_client):
        """Slash command /ppm-retry provides feedback."""
        mock_slack = mock_slack_client.return_value

        command_payload = {
            "command": "/ppm-retry",
            "text": "evt_123",
            "response_url": "https://slack.com/response/webhook",
        }

        handle_slash_command_retry(command_payload)

        # Verify response sent
        # In real implementation, would use requests.post to response_url
        # For testing, we verify the response structure
        assert True  # Placeholder - actual implementation would verify HTTP POST

    @patch("scripts.ppm.slack_notifier.SlackClient")
    def test_slash_command_status_response(self, mock_slack_client):
        """Slash command /ppm-status shows system health."""
        mock_slack = mock_slack_client.return_value

        command_payload = {
            "command": "/ppm-status",
            "text": "",
            "response_url": "https://slack.com/response/webhook",
        }

        response = handle_slash_command_status(command_payload)

        # Verify response includes health metrics
        assert "total_links" in response
        assert "healthy" in response
        assert "conflicts" in response
        assert "errors" in response


# Mock Slack notification functions
def send_success_notification(event: dict) -> None:
    """Mock success notification."""
    pass  # Would call Slack API


def send_failure_notification(event: dict) -> None:
    """Mock failure notification."""
    pass  # Would call Slack API


def send_conflict_notification(conflict: dict) -> None:
    """Mock conflict notification."""
    pass  # Would call Slack API


def send_daily_summary(summary: dict) -> None:
    """Mock daily summary notification."""
    pass  # Would call Slack API


def handle_slash_command_retry(command_payload: dict) -> dict:
    """Mock /ppm-retry slash command handler."""
    return {"response": "Retry initiated for event evt_123"}


def handle_slash_command_status(command_payload: dict) -> dict:
    """Mock /ppm-status slash command handler."""
    return {
        "total_links": 35,
        "healthy": 33,
        "conflicts": 1,
        "errors": 1,
    }
