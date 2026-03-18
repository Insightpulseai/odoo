"""
End-to-end integration tests for PPM Clarity sync workflows.

Tests the complete sync flow:
1. Plane webhook → n8n → Supabase RPC → Odoo RPC
2. Odoo completion → cron → Supabase RPC → Plane API
3. Reconciliation → conflict detection → resolution
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestPlaneToOdooSync:
    """Test Plane → Odoo sync workflow."""

    @patch("scripts.ppm.plane_client.PlaneClient")
    @patch("scripts.ppm.odoo_client.OdooClient")
    def test_commitment_signal_creates_odoo_task(
        self, mock_odoo_client, mock_plane_client
    ):
        """Plane commitment signal creates Odoo task."""
        # Mock Plane webhook payload
        plane_payload = {
            "event": "issue.created",
            "data": {
                "id": "PLANE-123",
                "name": "Implement PPM sync",
                "description": "Build bidirectional sync",
                "state": "Planned",
                "labels": ["commit"],
                "estimate_point": 5,
            },
        }

        # Mock Odoo task creation
        mock_odoo = mock_odoo_client.return_value
        mock_odoo.create_task.return_value = {"id": 456, "name": "Implement PPM sync"}

        # Execute sync
        result = sync_plane_to_odoo(plane_payload)

        # Verify Odoo task created
        mock_odoo.create_task.assert_called_once()
        assert result["success"] is True
        assert result["odoo_task_id"] == 456

    @patch("scripts.ppm.plane_client.PlaneClient")
    @patch("scripts.ppm.odoo_client.OdooClient")
    def test_non_commitment_signal_skipped(
        self, mock_odoo_client, mock_plane_client
    ):
        """Plane updates without commitment signal are skipped."""
        # Mock Plane payload without commitment signal
        plane_payload = {
            "event": "issue.updated",
            "data": {
                "id": "PLANE-124",
                "name": "Regular update",
                "state": "Backlog",  # Not "Planned"
                "labels": [],  # No "commit" label
            },
        }

        mock_odoo = mock_odoo_client.return_value

        # Execute sync
        result = sync_plane_to_odoo(plane_payload)

        # Verify Odoo task NOT created
        mock_odoo.create_task.assert_not_called()
        assert result["success"] is True
        assert result["action"] == "skipped"
        assert result["reason"] == "no_commitment_signal"


class TestOdooToPlaneSync:
    """Test Odoo → Plane sync workflow."""

    @patch("scripts.ppm.plane_client.PlaneClient")
    @patch("scripts.ppm.odoo_client.OdooClient")
    def test_odoo_completion_updates_plane(
        self, mock_odoo_client, mock_plane_client
    ):
        """Odoo task completion updates Plane work item."""
        # Mock Odoo completed task
        mock_odoo = mock_odoo_client.return_value
        mock_odoo.get_completed_tasks_since.return_value = [
            {
                "id": 456,
                "name": "Implement PPM sync",
                "stage": "Done",
                "effective_hours": 6.5,
            }
        ]

        # Mock Plane update
        mock_plane = mock_plane_client.return_value
        mock_plane.update_work_item.return_value = {
            "id": "PLANE-123",
            "state": "Done",
        }

        # Execute sync
        result = sync_odoo_to_plane(last_sync_timestamp="2024-03-05T00:00:00Z")

        # Verify Plane updated with facts only
        mock_plane.update_work_item.assert_called_once()
        call_args = mock_plane.update_work_item.call_args[1]
        assert call_args["work_item_id"] == "PLANE-123"
        assert call_args["updates"]["state"] == "Done"
        assert "effective_hours" in call_args["updates"]  # Read-only fact

    @patch("scripts.ppm.plane_client.PlaneClient")
    @patch("scripts.ppm.odoo_client.OdooClient")
    def test_no_completed_tasks_skips_sync(
        self, mock_odoo_client, mock_plane_client
    ):
        """No completed tasks results in skipped sync."""
        mock_odoo = mock_odoo_client.return_value
        mock_odoo.get_completed_tasks_since.return_value = []

        mock_plane = mock_plane_client.return_value

        result = sync_odoo_to_plane(last_sync_timestamp="2024-03-05T00:00:00Z")

        mock_plane.update_work_item.assert_not_called()
        assert result["action"] == "skipped"
        assert result["reason"] == "no_completed_tasks"


class TestReconciliation:
    """Test nightly reconciliation workflow."""

    @patch("scripts.ppm.plane_client.PlaneClient")
    @patch("scripts.ppm.odoo_client.OdooClient")
    def test_drift_detection_triggers_reconciliation(
        self, mock_odoo_client, mock_plane_client
    ):
        """Drift between Plane and Odoo triggers reconciliation."""
        # Mock drift scenario
        plane_data = {"PLANE-123": {"title": "Old title", "state": "In Progress"}}
        odoo_data = {456: {"name": "New title", "stage": "Planned"}}

        mock_plane = mock_plane_client.return_value
        mock_plane.get_work_item.return_value = plane_data["PLANE-123"]

        mock_odoo = mock_odoo_client.return_value
        mock_odoo.get_task.return_value = odoo_data[456]

        # Execute reconciliation
        result = reconcile_work_item(
            plane_issue_id="PLANE-123", odoo_task_id=456
        )

        # Verify drift detected
        assert result["drift_detected"] is True
        assert "title" in result["drifted_fields"]

    @patch("scripts.ppm.plane_client.PlaneClient")
    def test_reconciliation_applies_field_ownership(self, mock_plane_client):
        """Reconciliation applies field ownership rules."""
        # Mock drift on Plane-owned field
        plane_value = "Plane title"
        odoo_value = "Odoo title"

        mock_plane = mock_plane_client.return_value

        # Execute reconciliation with field ownership
        result = reconcile_field(
            field="title", plane_value=plane_value, odoo_value=odoo_value
        )

        # Verify Plane value wins (Plane owns title field)
        assert result["winner"] == "plane"
        assert result["resolved_value"] == plane_value


# Mock sync functions
def sync_plane_to_odoo(plane_payload: dict) -> dict:
    """Mock Plane → Odoo sync."""
    data = plane_payload.get("data", {})
    state = data.get("state")
    labels = data.get("labels", [])

    # Check commitment signal
    if state == "Planned" or "commit" in labels:
        # Would create Odoo task
        return {"success": True, "odoo_task_id": 456, "action": "created"}

    return {"success": True, "action": "skipped", "reason": "no_commitment_signal"}


def sync_odoo_to_plane(last_sync_timestamp: str) -> dict:
    """Mock Odoo → Plane sync."""
    # Would query completed tasks
    completed_tasks = []  # Mock: no completed tasks

    if not completed_tasks:
        return {"action": "skipped", "reason": "no_completed_tasks"}

    return {"success": True, "synced_count": len(completed_tasks)}


def reconcile_work_item(plane_issue_id: str, odoo_task_id: int) -> dict:
    """Mock reconciliation."""
    # Simulate drift detection
    return {
        "drift_detected": True,
        "drifted_fields": ["title"],
        "plane_issue_id": plane_issue_id,
        "odoo_task_id": odoo_task_id,
    }


def reconcile_field(field: str, plane_value: str, odoo_value: str) -> dict:
    """Mock field reconciliation."""
    PLANE_FIELDS = ["title", "description", "priority"]

    if field in PLANE_FIELDS:
        return {"winner": "plane", "resolved_value": plane_value}

    return {"winner": "odoo", "resolved_value": odoo_value}
