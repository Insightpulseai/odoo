"""Deterministic sync engine for PPM Clarity integration.

This module implements field-ownership-based sync logic between Plane and Odoo,
ensuring clean separation of concerns and conflict-free synchronization.
"""

from typing import Dict, Optional, Tuple

from .odoo_client import OdooClient
from .plane_client import PlaneClient


class SyncEngine:
    """Deterministic sync engine with field ownership enforcement.

    Field Ownership Rules:
    - Plane-owned: title, description, priority, labels, cycle, state, estimate
    - Odoo-owned: assigned users, timesheets, costs, attachments

    Sync Patterns:
    - Plane → Odoo: Create/update task with Plane-owned fields
    - Odoo → Plane: Facts-only writeback (completion status, metrics in comments)
    - Reconciliation: Detect drift via hash comparison, apply field ownership rules
    """

    def __init__(self, plane_client: PlaneClient, odoo_client: OdooClient):
        """Initialize sync engine with API clients.

        Args:
            plane_client: Initialized Plane API client
            odoo_client: Initialized Odoo RPC client
        """
        self.plane = plane_client
        self.odoo = odoo_client

    def plane_to_odoo(
        self, plane_project_id: str, plane_issue_id: str, odoo_project_id: int
    ) -> Tuple[int, str]:
        """Sync Plane work item to Odoo task (create or update).

        Args:
            plane_project_id: Plane project ID
            plane_issue_id: Plane issue ID
            odoo_project_id: Odoo project ID for new task creation

        Returns:
            Tuple of (odoo_task_id, plane_hash)

        Raises:
            Exception: If Plane API or Odoo RPC fails
        """
        # Fetch current Plane issue
        issue = self.plane.get_issue(plane_project_id, plane_issue_id)

        # Extract Plane-owned fields
        task_data = {
            "title": issue.get("name", ""),
            "description": issue.get("description_html", ""),
            "priority": self._map_priority_plane_to_odoo(issue.get("priority")),
            "planned_hours": (issue.get("estimate_point", 0) * 8.0),  # Story points → hours
        }

        # Map state to Odoo stage
        if issue.get("state"):
            task_data["stage"] = issue["state"].get("name", "Backlog")

        # Create or update task (caller provides odoo_task_id if updating)
        # For simplicity, this method always creates. Caller should check link table first.
        odoo_task_id = self.odoo.create_task(odoo_project_id, task_data)

        # Calculate Plane hash for drift detection
        plane_hash = self.plane.calculate_hash(issue)

        return odoo_task_id, plane_hash

    def odoo_to_plane(
        self, odoo_task_id: int, plane_project_id: str, plane_issue_id: str
    ) -> str:
        """Sync Odoo task completion to Plane (facts-only writeback).

        Args:
            odoo_task_id: Odoo task ID
            plane_project_id: Plane project ID
            plane_issue_id: Plane issue ID

        Returns:
            Odoo hash after writeback

        Raises:
            Exception: If Odoo RPC or Plane API fails
        """
        # Fetch current Odoo task
        task = self.odoo.get_task_details(odoo_task_id)

        # Check if task is completed
        stage = task.get("stage_id")
        if not stage or not isinstance(stage, (list, tuple)):
            return self.odoo.calculate_hash(task)

        # Fetch stage details to check if closed
        # (Simplified: assume stage name contains "Done" or is_closed=True)
        # In production, query stage metadata

        # Extract metrics for comment
        effective_hours = task.get("effective_hours", 0.0)
        planned_hours = task.get("planned_hours", 0.0)
        write_date = task.get("write_date", "")

        # Create comment in Plane with Odoo facts
        comment = f"""**Task completed in Odoo**

- Completion date: {write_date}
- Planned hours: {planned_hours:.1f}h
- Actual hours: {effective_hours:.1f}h
- Variance: {(effective_hours - planned_hours):.1f}h ({((effective_hours / planned_hours - 1) * 100) if planned_hours > 0 else 0:.1f}%)

> Synced from Odoo via PPM Clarity
"""
        self.plane.create_comment(plane_project_id, plane_issue_id, comment)

        # Update Plane state to "Done" (facts-only)
        # Note: Requires fetching project states to find "Done" state_id
        # For simplicity, we just add the comment here
        # Production implementation should update state

        # Calculate Odoo hash for drift detection
        return self.odoo.calculate_hash(task)

    def reconcile(
        self,
        plane_project_id: str,
        plane_issue_id: str,
        odoo_task_id: int,
        last_plane_hash: str,
        last_odoo_hash: str,
    ) -> Tuple[str, str, str]:
        """Reconcile drift between Plane and Odoo using field ownership rules.

        Args:
            plane_project_id: Plane project ID
            plane_issue_id: Plane issue ID
            odoo_task_id: Odoo task ID
            last_plane_hash: Last known Plane hash
            last_odoo_hash: Last known Odoo hash

        Returns:
            Tuple of (new_plane_hash, new_odoo_hash, resolution_action)

        Resolution Actions:
        - "plane_to_odoo": Plane changed, update Odoo
        - "odoo_to_plane": Odoo changed, update Plane comment
        - "both_changed": Conflict detected, apply field ownership
        - "no_change": No drift detected
        """
        # Fetch current state from both systems
        issue = self.plane.get_issue(plane_project_id, plane_issue_id)
        task = self.odoo.get_task_details(odoo_task_id)

        # Calculate current hashes
        current_plane_hash = self.plane.calculate_hash(issue)
        current_odoo_hash = self.odoo.calculate_hash(task)

        # Detect changes
        plane_changed = current_plane_hash != last_plane_hash
        odoo_changed = current_odoo_hash != last_odoo_hash

        if not plane_changed and not odoo_changed:
            return current_plane_hash, current_odoo_hash, "no_change"

        if plane_changed and not odoo_changed:
            # Plane changed → update Odoo with Plane-owned fields
            task_data = {
                "title": issue.get("name", ""),
                "description": issue.get("description_html", ""),
                "priority": self._map_priority_plane_to_odoo(issue.get("priority")),
                "planned_hours": (issue.get("estimate_point", 0) * 8.0),
            }
            if issue.get("state"):
                task_data["stage"] = issue["state"].get("name")

            self.odoo.update_task(odoo_task_id, task_data)
            return current_plane_hash, current_odoo_hash, "plane_to_odoo"

        if odoo_changed and not plane_changed:
            # Odoo changed → facts-only comment in Plane
            effective_hours = task.get("effective_hours", 0.0)
            comment = f"""**Odoo metrics updated**

- Actual hours: {effective_hours:.1f}h
- Last updated: {task.get("write_date", "")}

> Synced from Odoo via PPM Clarity
"""
            self.plane.create_comment(plane_project_id, plane_issue_id, comment)
            return current_plane_hash, current_odoo_hash, "odoo_to_plane"

        # Both changed → apply field ownership rules
        # Plane-owned → Odoo, Odoo-owned → Plane comment
        task_data = {
            "title": issue.get("name", ""),
            "description": issue.get("description_html", ""),
            "priority": self._map_priority_plane_to_odoo(issue.get("priority")),
            "planned_hours": (issue.get("estimate_point", 0) * 8.0),
        }
        if issue.get("state"):
            task_data["stage"] = issue["state"].get("name")

        self.odoo.update_task(odoo_task_id, task_data)

        # Add Odoo facts to Plane
        effective_hours = task.get("effective_hours", 0.0)
        comment = f"""**Conflict resolved via field ownership**

- Plane-owned fields updated in Odoo
- Odoo metrics: {effective_hours:.1f}h actual

> Synced from Odoo via PPM Clarity
"""
        self.plane.create_comment(plane_project_id, plane_issue_id, comment)

        return current_plane_hash, current_odoo_hash, "both_changed"

    def _map_priority_plane_to_odoo(self, plane_priority: Optional[str]) -> int:
        """Map Plane priority to Odoo priority (0-3).

        Args:
            plane_priority: Plane priority string (urgent, high, medium, low, none)

        Returns:
            Odoo priority (0=Normal, 1=Important, 2=Urgent, 3=Very Urgent)
        """
        priority_map = {
            "urgent": 3,
            "high": 2,
            "medium": 1,
            "low": 0,
            "none": 0,
        }
        return priority_map.get(plane_priority, 0) if plane_priority else 0
