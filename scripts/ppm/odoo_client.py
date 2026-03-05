"""Odoo XML-RPC client for PPM Clarity integration.

This module provides a Python client for interacting with Odoo's XML-RPC API
to manage projects and tasks, calculate field ownership hashes, and synchronize with Plane.
"""

import hashlib
import json
import os
import xmlrpc.client
from typing import Any, Dict, List, Optional


class OdooClient:
    """Client for Odoo external RPC with XML-RPC/JSON-RPC support.

    Field Ownership (Odoo-owned):
    - assigned_users (user_ids)
    - timesheets (timesheet_ids)
    - costs (effective_hours, cost calculations)
    - attachments (attachment_ids)
    - planned_hours (derived from Plane estimate, but managed in Odoo)
    """

    def __init__(
        self,
        url: Optional[str] = None,
        db: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Initialize Odoo client and authenticate.

        Args:
            url: Odoo server URL (defaults to ODOO_URL env var)
            db: Odoo database name (defaults to ODOO_DB env var)
            username: Odoo username (defaults to ODOO_USERNAME env var)
            password: Odoo password (defaults to ODOO_PASSWORD env var)

        Raises:
            ValueError: If authentication fails or credentials missing
        """
        self.url = url or os.getenv("ODOO_URL", "http://localhost:8069")
        self.db = db or os.getenv("ODOO_DB", "odoo")
        self.username = username or os.getenv("ODOO_USERNAME")
        self.password = password or os.getenv("ODOO_PASSWORD")

        if not self.username or not self.password:
            raise ValueError(
                "Odoo credentials not provided and not found in environment"
            )

        # Authenticate
        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.uid = common.authenticate(self.db, self.username, self.password, {})

        if not self.uid:
            raise ValueError(
                f"Authentication failed for user {self.username} on database {self.db}"
            )

        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def _execute(
        self,
        model: str,
        method: str,
        args: List[Any],
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Execute RPC method on Odoo model."""
        return self.models.execute_kw(
            self.db, self.uid, self.password, model, method, args, kwargs or {}
        )

    def create_project(
        self, name: str, description: str, stages: List[str]
    ) -> int:
        """Create Odoo project with aligned stages.

        Args:
            name: Project name
            description: Project description
            stages: List of stage names (e.g., ["Draft", "Backlog", "In Progress", "Done"])

        Returns:
            Created project ID
        """
        project_vals = {
            "name": name,
            "description": description,
            "type_ids": [
                (0, 0, {"name": stage, "sequence": i + 1})
                for i, stage in enumerate(stages)
            ],
            "allow_timesheets": True,
            "allow_billable": True,
        }
        return self._execute("project.project", "create", [project_vals])

    def create_task(self, project_id: int, data: Dict[str, Any]) -> int:
        """Create project.task from Plane work item.

        Args:
            project_id: Odoo project ID
            data: Task data with Plane-owned fields

        Returns:
            Created task ID
        """
        task_vals = {
            "name": data.get("title", "Untitled Task"),
            "description": data.get("description", ""),
            "project_id": project_id,
            "priority": str(data.get("priority", "0")),
            "planned_hours": data.get("planned_hours", 0.0),
        }

        # Map stage if provided
        if "stage" in data:
            stage_id = self._get_stage_id(project_id, data["stage"])
            if stage_id:
                task_vals["stage_id"] = stage_id

        return self._execute("project.task", "create", [task_vals])

    def update_task(self, task_id: int, data: Dict[str, Any]) -> bool:
        """Update existing task with Plane-owned fields only.

        Args:
            task_id: Odoo task ID
            data: Update data (only Plane-owned fields)

        Returns:
            True if update successful
        """
        update_vals = {}

        # Only update Plane-owned fields
        if "title" in data:
            update_vals["name"] = data["title"]
        if "description" in data:
            update_vals["description"] = data["description"]
        if "priority" in data:
            update_vals["priority"] = str(data["priority"])
        if "planned_hours" in data:
            update_vals["planned_hours"] = data["planned_hours"]

        # Handle stage mapping
        if "stage" in data:
            # Get task to find project
            task = self.get_task_details(task_id)
            project_id = task["project_id"][0] if task.get("project_id") else None
            if project_id:
                stage_id = self._get_stage_id(project_id, data["stage"])
                if stage_id:
                    update_vals["stage_id"] = stage_id

        if not update_vals:
            return True  # No changes needed

        self._execute("project.task", "write", [[task_id], update_vals])
        return True

    def get_task_details(self, task_id: int) -> Dict:
        """Get task with Odoo-owned fields (timesheets, costs, attachments).

        Args:
            task_id: Odoo task ID

        Returns:
            Task object with full details
        """
        fields = [
            "name",
            "description",
            "project_id",
            "stage_id",
            "priority",
            "user_ids",
            "timesheet_ids",
            "attachment_ids",
            "planned_hours",
            "effective_hours",
            "write_date",
        ]
        tasks = self._execute(
            "project.task", "read", [[task_id]], {"fields": fields}
        )
        return tasks[0] if tasks else {}

    def get_completed_tasks(
        self, since: str, project_ids: Optional[List[int]] = None
    ) -> List[Dict]:
        """Get tasks completed since a specific datetime.

        Args:
            since: ISO8601 datetime string (e.g., "2026-03-05 12:00:00")
            project_ids: Optional list of project IDs to filter

        Returns:
            List of completed task objects
        """
        domain = [("stage_id.is_closed", "=", True), ("write_date", ">=", since)]

        if project_ids:
            domain.append(("project_id", "in", project_ids))

        task_ids = self._execute("project.task", "search", [domain])
        if not task_ids:
            return []

        return self._execute(
            "project.task",
            "read",
            [task_ids],
            {
                "fields": [
                    "id",
                    "name",
                    "project_id",
                    "effective_hours",
                    "write_date",
                ]
            },
        )

    def calculate_hash(self, task: Dict) -> str:
        """Calculate deterministic hash of Odoo-owned fields.

        This hash is used to detect drift between Odoo and Plane.
        Only Odoo-owned fields are included to avoid false positives
        from Plane-owned field changes.

        Args:
            task: Odoo task object from get_task_details()

        Returns:
            SHA256 hex digest of canonical JSON representation
        """
        canonical_fields = {
            "users": sorted(
                [
                    user[0] if isinstance(user, (list, tuple)) else user
                    for user in task.get("user_ids", [])
                ]
            ),
            "timesheets": sorted(
                [
                    ts[0] if isinstance(ts, (list, tuple)) else ts
                    for ts in task.get("timesheet_ids", [])
                ]
            ),
            "attachments": sorted(
                [
                    att[0] if isinstance(att, (list, tuple)) else att
                    for att in task.get("attachment_ids", [])
                ]
            ),
            "planned_hours": task.get("planned_hours", 0.0),
            "effective_hours": task.get("effective_hours", 0.0),
        }
        # Deterministic JSON serialization (sorted keys, no whitespace)
        canonical_json = json.dumps(canonical_fields, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    def _get_stage_id(self, project_id: int, stage_name: str) -> Optional[int]:
        """Lookup stage ID by name in project.

        Args:
            project_id: Odoo project ID
            stage_name: Stage name to lookup

        Returns:
            Stage ID if found, None otherwise
        """
        # Get project stages
        project = self._execute(
            "project.project",
            "read",
            [[project_id]],
            {"fields": ["type_ids"]},
        )
        if not project:
            return None

        type_ids = project[0].get("type_ids", [])
        if not type_ids:
            return None

        # Search for stage by name
        stages = self._execute(
            "project.task.type",
            "read",
            [type_ids],
            {"fields": ["id", "name"]},
        )

        for stage in stages:
            if stage["name"] == stage_name:
                return stage["id"]

        return None
