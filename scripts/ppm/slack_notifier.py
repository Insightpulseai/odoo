"""Slack notification client for PPM Clarity sync events.

This module provides Slack notifications for sync operations, conflicts,
and reconciliation reports with interactive conflict resolution blocks.
"""

import os
from typing import Any, Dict, List, Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackNotifier:
    """Slack notification client with interactive Block Kit support.

    Notification Types:
    - Sync success: Simple message with metrics
    - Sync failure: Error details with retry options
    - Conflict: Interactive blocks with resolution buttons
    - Reconciliation report: Daily summary with conflict count
    """

    def __init__(
        self,
        token: Optional[str] = None,
        channel: Optional[str] = None,
    ):
        """Initialize Slack client.

        Args:
            token: Slack bot token (defaults to SLACK_BOT_TOKEN env var)
            channel: Default channel for notifications (defaults to SLACK_PPM_CHANNEL env var)
        """
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        self.channel = channel or os.getenv("SLACK_PPM_CHANNEL", "#ppm-clarity")

        if not self.token:
            raise ValueError(
                "SLACK_BOT_TOKEN not provided and not found in environment"
            )

        self.client = WebClient(token=self.token)

    def notify_sync_success(
        self,
        source: str,
        target: str,
        item_count: int,
        duration_ms: int,
        channel: Optional[str] = None,
    ) -> Dict:
        """Notify successful sync operation.

        Args:
            source: Source system (e.g., "Plane")
            target: Target system (e.g., "Odoo")
            item_count: Number of items synced
            duration_ms: Sync duration in milliseconds
            channel: Optional channel override

        Returns:
            Slack API response
        """
        message = (
            f":white_check_mark: *PPM Clarity Sync Success*\n"
            f"{source} → {target}\n"
            f"• Items synced: {item_count}\n"
            f"• Duration: {duration_ms}ms"
        )

        return self._send_message(message, channel=channel)

    def notify_sync_failure(
        self,
        source: str,
        target: str,
        error_message: str,
        item_id: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> Dict:
        """Notify sync failure with error details.

        Args:
            source: Source system (e.g., "Plane")
            target: Target system (e.g., "Odoo")
            error_message: Error message from sync operation
            item_id: Optional item ID that failed
            channel: Optional channel override

        Returns:
            Slack API response
        """
        message = (
            f":x: *PPM Clarity Sync Failed*\n"
            f"{source} → {target}\n"
            f"• Error: {error_message}"
        )

        if item_id:
            message += f"\n• Item ID: `{item_id}`"

        return self._send_message(message, channel=channel, color="danger")

    def notify_conflict(
        self,
        plane_project_id: str,
        plane_issue_id: str,
        odoo_task_id: int,
        conflict_fields: List[str],
        channel: Optional[str] = None,
    ) -> Dict:
        """Notify sync conflict with interactive resolution blocks.

        Args:
            plane_project_id: Plane project ID
            plane_issue_id: Plane issue ID
            odoo_task_id: Odoo task ID
            conflict_fields: List of conflicting field names
            channel: Optional channel override

        Returns:
            Slack API response with interactive blocks
        """
        blocks = self._create_conflict_blocks(
            plane_project_id=plane_project_id,
            plane_issue_id=plane_issue_id,
            odoo_task_id=odoo_task_id,
            conflict_fields=conflict_fields,
        )

        try:
            return self.client.chat_postMessage(
                channel=channel or self.channel,
                blocks=blocks,
                text=f"Sync conflict detected: Plane {plane_issue_id} ↔ Odoo Task {odoo_task_id}",
            )
        except SlackApiError as e:
            raise Exception(f"Slack API error: {e.response['error']}")

    def notify_reconciliation_report(
        self,
        total_conflicts: int,
        resolved_conflicts: int,
        failed_conflicts: int,
        duration_ms: int,
        channel: Optional[str] = None,
    ) -> Dict:
        """Notify nightly reconciliation summary.

        Args:
            total_conflicts: Total conflicts detected
            resolved_conflicts: Successfully resolved conflicts
            failed_conflicts: Failed conflict resolutions
            duration_ms: Reconciliation duration in milliseconds
            channel: Optional channel override

        Returns:
            Slack API response
        """
        success_rate = (
            (resolved_conflicts / total_conflicts * 100) if total_conflicts > 0 else 100
        )
        color = "good" if success_rate >= 90 else "warning" if success_rate >= 70 else "danger"

        message = (
            f"*PPM Clarity Nightly Reconciliation*\n"
            f"• Total conflicts: {total_conflicts}\n"
            f"• Resolved: {resolved_conflicts}\n"
            f"• Failed: {failed_conflicts}\n"
            f"• Success rate: {success_rate:.1f}%\n"
            f"• Duration: {duration_ms}ms"
        )

        return self._send_message(message, channel=channel, color=color)

    def _create_conflict_blocks(
        self,
        plane_project_id: str,
        plane_issue_id: str,
        odoo_task_id: int,
        conflict_fields: List[str],
    ) -> List[Dict]:
        """Create interactive Slack blocks for conflict resolution.

        Args:
            plane_project_id: Plane project ID
            plane_issue_id: Plane issue ID
            odoo_task_id: Odoo task ID
            conflict_fields: List of conflicting field names

        Returns:
            List of Slack Block Kit blocks
        """
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":warning: Sync Conflict Detected",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Plane Issue:*\n{plane_project_id}/{plane_issue_id}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Odoo Task:*\n#{odoo_task_id}",
                    },
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Conflicting Fields:*\n{', '.join(conflict_fields)}",
                },
            },
            {
                "type": "divider",
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Resolution Strategy:*\n"
                    "Field ownership rules will be applied automatically:\n"
                    "• Plane-owned → Update Odoo\n"
                    "• Odoo-owned → Comment in Plane",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View in Plane",
                            "emoji": True,
                        },
                        "url": f"https://plane.insightpulseai.com/{plane_project_id}/issues/{plane_issue_id}",
                        "action_id": "view_plane",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View in Odoo",
                            "emoji": True,
                        },
                        "url": f"https://insightpulseai.com/web#id={odoo_task_id}&model=project.task",
                        "action_id": "view_odoo",
                    },
                ],
            },
        ]

    def _send_message(
        self,
        message: str,
        channel: Optional[str] = None,
        color: Optional[str] = None,
    ) -> Dict:
        """Send simple message to Slack channel.

        Args:
            message: Message text (supports Markdown)
            channel: Optional channel override
            color: Optional color for attachment (good, warning, danger)

        Returns:
            Slack API response
        """
        try:
            if color:
                # Use legacy attachment for colored messages
                return self.client.chat_postMessage(
                    channel=channel or self.channel,
                    attachments=[
                        {
                            "color": color,
                            "text": message,
                            "mrkdwn_in": ["text"],
                        }
                    ],
                    text=message.split("\n")[0],  # Fallback text
                )
            else:
                return self.client.chat_postMessage(
                    channel=channel or self.channel,
                    text=message,
                )
        except SlackApiError as e:
            raise Exception(f"Slack API error: {e.response['error']}")
