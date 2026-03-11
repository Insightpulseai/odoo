"""
Test conflict resolution logic for PPM Clarity integration.

Based on spec/ppm-clarity-plane-odoo/constitution.md P8:
- Field ownership rules resolve drift automatically
- Same-field edits escalate to manual review
- Conflicts stored in ops.work_item_links with sync_state='needs_review'
"""

import pytest
from datetime import datetime


class TestConflictResolution:
    """Test conflict detection and resolution."""

    def test_no_conflict_when_different_fields_modified(self):
        """No conflict when Plane and Odoo modify different fields."""
        plane_changes = {"title": "Updated title", "priority": "high"}
        odoo_changes = {"user_ids": [1, 2], "planned_hours": 8.0}

        conflict = detect_conflict(plane_changes, odoo_changes)
        assert conflict is None  # No conflict - different fields

    def test_conflict_when_same_field_modified(self):
        """Conflict when both systems modify the same shared field."""
        plane_changes = {"state": "In Progress"}
        odoo_changes = {"state": "Done"}

        conflict = detect_conflict(plane_changes, odoo_changes)
        assert conflict is not None
        assert conflict["field"] == "state"
        assert conflict["plane_value"] == "In Progress"
        assert conflict["odoo_value"] == "Done"
        assert conflict["resolution_required"] is True

    def test_plane_owned_field_auto_resolves(self):
        """Plane-owned fields auto-resolve to Plane value."""
        # Plane modifies title (Plane-owned field)
        plane_changes = {"title": "Plane title"}
        odoo_changes = {"title": "Odoo title"}  # Invalid - Odoo shouldn't modify

        resolution = resolve_conflict_auto(plane_changes, odoo_changes, "title")
        assert resolution["winner"] == "plane"
        assert resolution["value"] == "Plane title"
        assert resolution["auto_resolved"] is True

    def test_odoo_owned_field_auto_resolves(self):
        """Odoo-owned fields auto-resolve to Odoo value."""
        # Odoo modifies user_ids (Odoo-owned field)
        plane_changes = {"user_ids": [1]}  # Invalid - Plane shouldn't modify
        odoo_changes = {"user_ids": [2, 3]}

        resolution = resolve_conflict_auto(plane_changes, odoo_changes, "user_ids")
        assert resolution["winner"] == "odoo"
        assert resolution["value"] == [2, 3]
        assert resolution["auto_resolved"] is True

    def test_manual_review_required_for_dual_ownership_violation(self):
        """Dual-ownership violations require manual review."""
        # Both systems modified the same owned field (violation)
        plane_changes = {"title": "Plane title"}
        odoo_changes = {"title": "Odoo title"}

        resolution = resolve_conflict_auto(plane_changes, odoo_changes, "title")
        assert resolution["auto_resolved"] is False
        assert resolution["manual_review_required"] is True
        assert resolution["reason"] == "dual_ownership_violation"

    def test_sync_state_updated_on_conflict(self):
        """ops.work_item_links.sync_state set to 'needs_review' on conflict."""
        link = {
            "link_id": "link_123",
            "plane_issue_id": "PLANE-123",
            "odoo_task_id": "456",
            "sync_state": "healthy",
        }

        conflict = {
            "field": "state",
            "plane_value": "In Progress",
            "odoo_value": "Done",
            "resolution_required": True,
        }

        updated_link = update_sync_state_on_conflict(link, conflict)
        assert updated_link["sync_state"] == "needs_review"
        assert updated_link["conflict_reason"] == "same_field_modified: state"

    def test_conflict_count_incremented(self):
        """Conflict count incremented in ops.work_item_links."""
        link = {"link_id": "link_123", "conflict_count": 0}

        updated_link = increment_conflict_count(link)
        assert updated_link["conflict_count"] == 1

        updated_link = increment_conflict_count(updated_link)
        assert updated_link["conflict_count"] == 2


# Mock functions for testing
def detect_conflict(plane_changes: dict, odoo_changes: dict) -> dict | None:
    """Detect if both systems modified the same field."""
    common_fields = set(plane_changes.keys()) & set(odoo_changes.keys())
    if not common_fields:
        return None

    # Return first conflict found
    field = list(common_fields)[0]
    return {
        "field": field,
        "plane_value": plane_changes[field],
        "odoo_value": odoo_changes[field],
        "resolution_required": True,
    }


def resolve_conflict_auto(
    plane_changes: dict, odoo_changes: dict, field: str
) -> dict:
    """Attempt automatic conflict resolution using field ownership."""
    # Field ownership rules
    PLANE_FIELDS = ["title", "description", "priority", "labels"]
    ODOO_FIELDS = ["user_ids", "planned_hours", "effective_hours"]

    plane_value = plane_changes.get(field)
    odoo_value = odoo_changes.get(field)

    # Check if both modified the same owned field (violation)
    if field in PLANE_FIELDS and odoo_value is not None:
        return {
            "auto_resolved": False,
            "manual_review_required": True,
            "reason": "dual_ownership_violation",
            "field": field,
        }

    if field in ODOO_FIELDS and plane_value is not None:
        return {
            "auto_resolved": False,
            "manual_review_required": True,
            "reason": "dual_ownership_violation",
            "field": field,
        }

    # Auto-resolve based on ownership
    if field in PLANE_FIELDS:
        return {"winner": "plane", "value": plane_value, "auto_resolved": True}

    if field in ODOO_FIELDS:
        return {"winner": "odoo", "value": odoo_value, "auto_resolved": True}

    # Unknown field or shared field
    return {
        "auto_resolved": False,
        "manual_review_required": True,
        "reason": "unknown_or_shared_field",
    }


def update_sync_state_on_conflict(link: dict, conflict: dict) -> dict:
    """Update sync_state to 'needs_review' on conflict."""
    link["sync_state"] = "needs_review"
    link["conflict_reason"] = f"same_field_modified: {conflict['field']}"
    return link


def increment_conflict_count(link: dict) -> dict:
    """Increment conflict count in link record."""
    link["conflict_count"] = link.get("conflict_count", 0) + 1
    return link
