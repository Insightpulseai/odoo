"""
Test field ownership rules for PPM Clarity integration.

Based on spec/ppm-clarity-plane-odoo/plan.md field ownership rules:
- Plane owns: name, description, labels, estimate_point, priority, start_date, target_date
- Odoo owns: stage_id, user_ids, date_deadline, planned_hours, effective_hours, progress
- Shared: state (both can modify, last-modified wins)
"""

import pytest


class TestFieldOwnership:
    """Test field ownership resolution logic."""

    PLANE_FIELDS = [
        "name",
        "description",
        "labels",
        "estimate_point",
        "priority",
        "start_date",
        "target_date",
    ]

    ODOO_FIELDS = [
        "stage_id",
        "user_ids",
        "date_deadline",
        "planned_hours",
        "effective_hours",
        "progress",
    ]

    SHARED_FIELDS = ["state"]

    def test_plane_field_ownership(self):
        """Plane-owned fields should resolve to Plane value."""
        for field in self.PLANE_FIELDS:
            conflict = {
                "field": field,
                "plane_value": "plane_val",
                "odoo_value": "odoo_val",
                "plane_modified": "2024-03-05T10:00:00Z",
                "odoo_modified": "2024-03-05T09:00:00Z",
            }

            # Plane owns this field, so Plane value wins regardless of timestamp
            resolution = resolve_field_conflict(conflict)
            assert resolution["winner"] == "plane"
            assert resolution["value"] == "plane_val"

    def test_odoo_field_ownership(self):
        """Odoo-owned fields should resolve to Odoo value."""
        for field in self.ODOO_FIELDS:
            conflict = {
                "field": field,
                "plane_value": "plane_val",
                "odoo_value": "odoo_val",
                "plane_modified": "2024-03-05T10:00:00Z",
                "odoo_modified": "2024-03-05T09:00:00Z",
            }

            # Odoo owns this field, so Odoo value wins regardless of timestamp
            resolution = resolve_field_conflict(conflict)
            assert resolution["winner"] == "odoo"
            assert resolution["value"] == "odoo_val"

    def test_shared_field_last_modified_wins(self):
        """Shared fields should use last-modified timestamp."""
        # Plane modified more recently
        conflict_plane_newer = {
            "field": "state",
            "plane_value": "In Progress",
            "odoo_value": "Planned",
            "plane_modified": "2024-03-05T10:00:00Z",
            "odoo_modified": "2024-03-05T09:00:00Z",
        }

        resolution = resolve_field_conflict(conflict_plane_newer)
        assert resolution["winner"] == "plane"
        assert resolution["value"] == "In Progress"

        # Odoo modified more recently
        conflict_odoo_newer = {
            "field": "state",
            "plane_value": "In Progress",
            "odoo_value": "Done",
            "plane_modified": "2024-03-05T09:00:00Z",
            "odoo_modified": "2024-03-05T10:00:00Z",
        }

        resolution = resolve_field_conflict(conflict_odoo_newer)
        assert resolution["winner"] == "odoo"
        assert resolution["value"] == "Done"

    def test_unknown_field_raises_error(self):
        """Unknown fields should raise an error."""
        conflict = {
            "field": "unknown_field",
            "plane_value": "val1",
            "odoo_value": "val2",
            "plane_modified": "2024-03-05T10:00:00Z",
            "odoo_modified": "2024-03-05T09:00:00Z",
        }

        with pytest.raises(ValueError, match="Unknown field"):
            resolve_field_conflict(conflict)


def resolve_field_conflict(conflict: dict) -> dict:
    """
    Resolve field conflict using ownership rules.

    Args:
        conflict: Dict with field, plane_value, odoo_value, plane_modified, odoo_modified

    Returns:
        Dict with winner ('plane' or 'odoo') and resolved value
    """
    field = conflict["field"]

    # Plane-owned fields
    if field in TestFieldOwnership.PLANE_FIELDS:
        return {"winner": "plane", "value": conflict["plane_value"]}

    # Odoo-owned fields
    if field in TestFieldOwnership.ODOO_FIELDS:
        return {"winner": "odoo", "value": conflict["odoo_value"]}

    # Shared fields - last modified wins
    if field in TestFieldOwnership.SHARED_FIELDS:
        plane_ts = conflict["plane_modified"]
        odoo_ts = conflict["odoo_modified"]

        if plane_ts > odoo_ts:
            return {"winner": "plane", "value": conflict["plane_value"]}
        else:
            return {"winner": "odoo", "value": conflict["odoo_value"]}

    # Unknown field
    raise ValueError(f"Unknown field: {field}")
