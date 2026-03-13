# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Odoo XML-RPC client for PPM Clarity sync.

Handles task creation, updates, and hash calculation for Odoo-owned fields.
Field ownership: assigned users, timesheets, costs, attachments, chatter.
"""

import hashlib
import json
import logging
import os
import xmlrpc.client

_logger = logging.getLogger(__name__)


class OdooClient:
    """Odoo external RPC client for project.task operations."""

    def __init__(self, url=None, db=None, username=None, password=None):
        self.url = url or os.environ.get("ODOO_URL", "https://insightpulseai.com/odoo")
        self.db = db or os.environ.get("ODOO_DB", "odoo")
        username = username or os.environ.get("ODOO_USER", "")
        password = password or os.environ.get("ODOO_PASSWORD", "")

        common = xmlrpc.client.ServerProxy(
            "%s/xmlrpc/2/common" % self.url, allow_none=True
        )
        self.uid = common.authenticate(self.db, username, password, {})
        if not self.uid:
            raise ConnectionError("Odoo authentication failed for user: %s" % username)

        self.password = password
        self.models = xmlrpc.client.ServerProxy(
            "%s/xmlrpc/2/object" % self.url, allow_none=True
        )
        _logger.info("OdooClient connected: url=%s db=%s uid=%s", self.url, self.db, self.uid)

    def _execute(self, model, method, *args, **kwargs):
        """Execute an Odoo RPC call."""
        return self.models.execute_kw(
            self.db, self.uid, self.password, model, method, *args, **kwargs
        )

    # ── Project operations ────────────────────────────────────────────

    def create_project(self, name, stages=None):
        """Create project.project with optional stage names.

        Args:
            name: Project name.
            stages: List of stage names (default: PPM Clarity template stages).

        Returns:
            int: project.project ID.
        """
        if stages is None:
            stages = [
                "Backlog", "Triage", "Planned",
                "In Progress", "Review", "Done", "Cancelled",
            ]

        project_id = self._execute(
            "project.project", "create",
            [{"name": name, "allow_timesheets": True}],
        )

        # Create stages aligned with Plane states
        for seq, stage_name in enumerate(stages, start=1):
            existing = self._execute(
                "project.task.type", "search",
                [[("name", "=", stage_name), ("project_ids", "in", [project_id])]],
            )
            if not existing:
                self._execute(
                    "project.task.type", "create",
                    [{"name": stage_name, "sequence": seq, "project_ids": [(4, project_id)]}],
                )

        _logger.info("Created Odoo project: id=%s name=%s", project_id, name)
        return project_id

    # ── Task operations ───────────────────────────────────────────────

    def create_task(self, project_id, data):
        """Create project.task from Plane commitment signal.

        Args:
            project_id: Odoo project.project ID.
            data: Dict with title, description, priority (Plane-owned fields).

        Returns:
            int: project.task ID.
        """
        stage_id = self._get_stage_id(project_id, data.get("state", "Backlog"))

        priority_map = {"urgent": "1", "high": "1", "medium": "0", "low": "0", "none": "0"}
        priority = priority_map.get(data.get("priority", "none"), "0")

        vals = {
            "name": data["title"],
            "description": data.get("description", ""),
            "project_id": project_id,
            "stage_id": stage_id,
            "priority": priority,
        }

        task_id = self._execute("project.task", "create", [vals])
        _logger.info("Created Odoo task: id=%s project=%s title=%s", task_id, project_id, data["title"])
        return task_id

    def update_task(self, task_id, data):
        """Update project.task with Plane-owned field changes.

        Args:
            task_id: Odoo project.task ID.
            data: Dict with fields to update.

        Returns:
            bool: True if update succeeded.
        """
        vals = {}
        if "title" in data:
            vals["name"] = data["title"]
        if "description" in data:
            vals["description"] = data["description"]
        if "state" in data:
            task = self._execute(
                "project.task", "read", [task_id], {"fields": ["project_id"]},
            )
            if task:
                project_id = task[0]["project_id"][0] if task[0].get("project_id") else None
                if project_id:
                    vals["stage_id"] = self._get_stage_id(project_id, data["state"])
        if "priority" in data:
            priority_map = {"urgent": "1", "high": "1", "medium": "0", "low": "0", "none": "0"}
            vals["priority"] = priority_map.get(data["priority"], "0")

        if vals:
            self._execute("project.task", "write", [[task_id], vals])
            _logger.info("Updated Odoo task: id=%s fields=%s", task_id, list(vals.keys()))

        return True

    def get_task_details(self, task_id):
        """Get task with Odoo-owned fields for hash calculation.

        Returns:
            dict: Task details including timesheets, user assignments.
        """
        fields = [
            "name", "description", "project_id", "stage_id",
            "user_ids", "priority", "timesheet_ids",
            "date_deadline", "kanban_state",
        ]
        tasks = self._execute("project.task", "read", [task_id], {"fields": fields})
        if not tasks:
            return None
        return tasks[0]

    def get_completed_tasks(self, project_id, since_dt=None):
        """Get tasks in 'Done' stage for Odoo → Plane completion signal.

        Args:
            project_id: Odoo project.project ID.
            since_dt: ISO datetime string; only return tasks completed after this time.

        Returns:
            list[dict]: Completed task records.
        """
        domain = [
            ("project_id", "=", project_id),
            ("stage_id.name", "=", "Done"),
        ]
        if since_dt:
            domain.append(("write_date", ">=", since_dt))

        task_ids = self._execute("project.task", "search", [domain])
        if not task_ids:
            return []

        return self._execute(
            "project.task", "read", [task_ids],
            {"fields": ["name", "stage_id", "user_ids", "write_date"]},
        )

    # ── Hash calculation (Odoo-owned fields) ──────────────────────────

    @staticmethod
    def calculate_hash(task):
        """Calculate deterministic SHA-256 hash of Odoo-owned fields.

        Odoo owns: assigned users, timesheets, costs, attachments.
        Hash changes only when Odoo-side data changes.
        """
        owned_data = {
            "user_ids": sorted(task.get("user_ids", [])),
            "timesheet_ids": sorted(task.get("timesheet_ids", [])),
            "stage_name": task.get("stage_id", [0, ""])[1] if isinstance(task.get("stage_id"), (list, tuple)) else str(task.get("stage_id", "")),
            "kanban_state": task.get("kanban_state", ""),
        }
        canonical = json.dumps(owned_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    # ── Helpers ───────────────────────────────────────────────────────

    def _get_stage_id(self, project_id, stage_name):
        """Get or create a stage by name for a project."""
        stages = self._execute(
            "project.task.type", "search_read",
            [[("name", "=", stage_name), ("project_ids", "in", [project_id])]],
            {"fields": ["id"], "limit": 1},
        )
        if stages:
            return stages[0]["id"]

        # Fallback: search without project filter
        stages = self._execute(
            "project.task.type", "search_read",
            [[("name", "=", stage_name)]],
            {"fields": ["id"], "limit": 1},
        )
        if stages:
            return stages[0]["id"]

        # Create if not found
        return self._execute(
            "project.task.type", "create",
            [{"name": stage_name, "project_ids": [(4, project_id)]}],
        )
