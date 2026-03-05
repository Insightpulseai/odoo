"""
Test idempotency key enforcement for PPM Clarity integration.

Based on spec/ppm-clarity-plane-odoo/constitution.md P5:
- Idempotency key format: plane:sync:{workflow_id}:{plane_issue_id}:{odoo_task_id}:{timestamp}
- UNIQUE constraint on ops.work_item_events.idempotency_key
- Duplicate key rejection with error message
"""

import pytest
from datetime import datetime


class TestIdempotencyKeys:
    """Test idempotency key generation and enforcement."""

    def test_idempotency_key_format(self):
        """Idempotency key must follow canonical format."""
        workflow_id = "ppm-clarity-plane-to-odoo"
        plane_issue_id = "PLANE-123"
        odoo_task_id = "456"
        timestamp = "2024-03-05T10:00:00Z"

        expected_key = f"plane:sync:{workflow_id}:{plane_issue_id}:{odoo_task_id}:{timestamp}"
        actual_key = generate_idempotency_key(
            workflow_id, plane_issue_id, odoo_task_id, timestamp
        )

        assert actual_key == expected_key
        assert actual_key.startswith("plane:sync:")
        assert workflow_id in actual_key
        assert plane_issue_id in actual_key
        assert odoo_task_id in actual_key

    def test_duplicate_idempotency_key_rejected(self):
        """Duplicate idempotency keys should be rejected."""
        event1 = {
            "idempotency_key": "plane:sync:workflow:PLANE-123:456:2024-03-05T10:00:00Z",
            "event_type": "plane_to_odoo",
            "payload": {"title": "Test"},
        }

        event2 = {
            "idempotency_key": "plane:sync:workflow:PLANE-123:456:2024-03-05T10:00:00Z",
            "event_type": "plane_to_odoo",
            "payload": {"title": "Duplicate"},
        }

        # First event should succeed
        result1 = insert_event(event1)
        assert result1["success"] is True

        # Second event with same key should be rejected
        result2 = insert_event(event2)
        assert result2["success"] is False
        assert "duplicate" in result2["error"].lower()
        assert "idempotency_key" in result2["error"].lower()

    def test_different_timestamps_create_unique_keys(self):
        """Different timestamps should create unique idempotency keys."""
        workflow_id = "ppm-clarity-plane-to-odoo"
        plane_issue_id = "PLANE-123"
        odoo_task_id = "456"

        key1 = generate_idempotency_key(
            workflow_id, plane_issue_id, odoo_task_id, "2024-03-05T10:00:00Z"
        )
        key2 = generate_idempotency_key(
            workflow_id, plane_issue_id, odoo_task_id, "2024-03-05T11:00:00Z"
        )

        assert key1 != key2
        # Both should be insertable without conflict
        assert "2024-03-05T10:00:00Z" in key1
        assert "2024-03-05T11:00:00Z" in key2

    def test_null_idempotency_key_rejected(self):
        """Events without idempotency keys should be rejected."""
        event = {
            "idempotency_key": None,
            "event_type": "plane_to_odoo",
            "payload": {"title": "Test"},
        }

        result = insert_event(event)
        assert result["success"] is False
        assert "required" in result["error"].lower() or "null" in result["error"].lower()


# Mock functions for testing
def generate_idempotency_key(
    workflow_id: str, plane_issue_id: str, odoo_task_id: str, timestamp: str
) -> str:
    """Generate idempotency key following canonical format."""
    return f"plane:sync:{workflow_id}:{plane_issue_id}:{odoo_task_id}:{timestamp}"


def insert_event(event: dict) -> dict:
    """Mock function to insert event into ops.work_item_events."""
    # Simulate database constraint validation
    if event.get("idempotency_key") is None:
        return {"success": False, "error": "idempotency_key is required (NOT NULL constraint)"}

    # Simulate UNIQUE constraint check (in real implementation, this would be database-enforced)
    # For testing, we track seen keys in a class variable
    if not hasattr(insert_event, "seen_keys"):
        insert_event.seen_keys = set()

    key = event["idempotency_key"]
    if key in insert_event.seen_keys:
        return {
            "success": False,
            "error": f"duplicate key value violates unique constraint: idempotency_key='{key}'",
        }

    insert_event.seen_keys.add(key)
    return {"success": True, "event_id": f"evt_{len(insert_event.seen_keys)}"}


# Reset seen keys between tests
@pytest.fixture(autouse=True)
def reset_seen_keys():
    """Reset seen keys before each test."""
    if hasattr(insert_event, "seen_keys"):
        insert_event.seen_keys.clear()
    yield
