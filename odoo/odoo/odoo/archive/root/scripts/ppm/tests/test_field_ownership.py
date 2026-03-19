# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Tests for field ownership contract enforcement."""

import unittest

from scripts.ppm.odoo_client import OdooClient
from scripts.ppm.plane_mcp_client import PlaneMCPClient


class TestPlaneHash(unittest.TestCase):
    """Plane hash must only include Plane-owned fields."""

    def test_hash_includes_name(self):
        issue_a = {"name": "Feature A", "description_html": "", "priority": "high",
                    "labels": [], "cycle_id": "", "state_id": "s1"}
        issue_b = {"name": "Feature B", "description_html": "", "priority": "high",
                    "labels": [], "cycle_id": "", "state_id": "s1"}
        self.assertNotEqual(
            PlaneMCPClient.calculate_hash(issue_a),
            PlaneMCPClient.calculate_hash(issue_b),
        )

    def test_hash_ignores_odoo_fields(self):
        """Plane hash must NOT change when non-owned fields change."""
        issue = {"name": "X", "description_html": "", "priority": "none",
                 "labels": [], "cycle_id": "", "state_id": "s1"}
        # Add Odoo-owned fields — hash must stay the same
        issue_with_odoo = {**issue, "assignees": ["user1"], "time_logged": 5.5}
        self.assertEqual(
            PlaneMCPClient.calculate_hash(issue),
            PlaneMCPClient.calculate_hash(issue_with_odoo),
        )

    def test_hash_deterministic(self):
        issue = {"name": "X", "description_html": "desc", "priority": "high",
                 "labels": ["l2", "l1"], "cycle_id": "c1", "state_id": "s1"}
        h1 = PlaneMCPClient.calculate_hash(issue)
        h2 = PlaneMCPClient.calculate_hash(issue)
        self.assertEqual(h1, h2)

    def test_hash_label_order_insensitive(self):
        issue_a = {"name": "X", "description_html": "", "priority": "none",
                   "labels": ["l1", "l2"], "cycle_id": "", "state_id": "s1"}
        issue_b = {"name": "X", "description_html": "", "priority": "none",
                   "labels": ["l2", "l1"], "cycle_id": "", "state_id": "s1"}
        self.assertEqual(
            PlaneMCPClient.calculate_hash(issue_a),
            PlaneMCPClient.calculate_hash(issue_b),
        )


class TestOdooHash(unittest.TestCase):
    """Odoo hash must only include Odoo-owned fields."""

    def test_hash_includes_user_ids(self):
        task_a = {"user_ids": [1, 2], "timesheet_ids": [], "stage_id": (1, "Done"),
                  "kanban_state": "normal"}
        task_b = {"user_ids": [3], "timesheet_ids": [], "stage_id": (1, "Done"),
                  "kanban_state": "normal"}
        self.assertNotEqual(
            OdooClient.calculate_hash(task_a),
            OdooClient.calculate_hash(task_b),
        )

    def test_hash_ignores_plane_fields(self):
        """Odoo hash must NOT change when Plane-owned fields change."""
        task = {"user_ids": [1], "timesheet_ids": [], "stage_id": (1, "Done"),
                "kanban_state": "normal"}
        task_with_plane = {**task, "name": "Changed Title", "description": "new"}
        self.assertEqual(
            OdooClient.calculate_hash(task),
            OdooClient.calculate_hash(task_with_plane),
        )

    def test_hash_deterministic(self):
        task = {"user_ids": [2, 1], "timesheet_ids": [10, 20],
                "stage_id": (5, "Review"), "kanban_state": "done"}
        self.assertEqual(
            OdooClient.calculate_hash(task),
            OdooClient.calculate_hash(task),
        )

    def test_hash_user_order_insensitive(self):
        task_a = {"user_ids": [1, 2], "timesheet_ids": [], "stage_id": (1, "Done"),
                  "kanban_state": "normal"}
        task_b = {"user_ids": [2, 1], "timesheet_ids": [], "stage_id": (1, "Done"),
                  "kanban_state": "normal"}
        self.assertEqual(
            OdooClient.calculate_hash(task_a),
            OdooClient.calculate_hash(task_b),
        )


if __name__ == "__main__":
    unittest.main()
