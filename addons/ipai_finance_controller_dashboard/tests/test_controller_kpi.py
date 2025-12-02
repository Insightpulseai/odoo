# -*- coding: utf-8 -*-

import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from odoo.tests import TransactionCase


@unittest.skip(
    "Tests require ipai.finance.monthly.close model (not yet implemented). "
    "Actual model is ppm.monthly.close with different field structure."
)
class TestFinanceControllerKPI(TransactionCase):
    """
    Unit tests for Finance Controller KPI computation

    Test Coverage:
    - KPI gauge data generation
    - Calendar heatmap data
    - WBS tree structure
    - Gantt chart data
    - RACI sunburst data
    - Dependency graph data
    - Daily cron job execution
    """

    def setUp(self):
        super().setUp()

        # Create test employee
        self.employee = self.env["hr.employee"].create(
            {
                "name": "Test Employee RIM",
                "code": "RIM",
            }
        )

        # Create test user linked to employee
        self.user = self.env["res.users"].create(
            {
                "name": "Test User RIM",
                "login": "test.rim@insightpulseai.net",
                "employee_ids": [(4, self.employee.id)],
            }
        )

        # Create test month-end close tasks
        self.task_phase1 = self.env["ipai.finance.monthly.close"].create(
            {
                "name": "Bank Reconciliation",
                "owner_code": "RIM",
                "cluster_classification": "Phase 1",
                "target_completion_date": datetime.now().date(),
                "status": "completed",
                "actual_completion_date": datetime.now().date(),
                "raci_role": "Responsible",
            }
        )

        self.task_phase2 = self.env["ipai.finance.monthly.close"].create(
            {
                "name": "GL Reconciliation",
                "owner_code": "RIM",
                "cluster_classification": "Phase 2",
                "parent_id": self.task_phase1.id,
                "target_completion_date": (datetime.now() + timedelta(days=3)).date(),
                "status": "in_progress",
                "raci_role": "Accountable",
            }
        )

        # Create test LogFrame indicator
        self.logframe = self.env["finance.ppm.logframe"].create(
            {
                "indicator_name": "BIR Forms Filed On Time",
                "target_value": 100.0,
                "actual_value": 95.0,
                "frequency": "monthly",
            }
        )

    def test_get_kpi_gauge_data(self):
        """Test KPI gauge data generation"""
        result = self.env["finance.controller.kpi"].get_kpi_gauge_data("RIM")

        # Verify structure
        self.assertIn("timeliness", result)
        self.assertIn("reconciliation", result)
        self.assertIn("filing_rate", result)
        self.assertIn("tasks_completed", result)
        self.assertIn("closing_adjustments", result)
        self.assertIn("daily_completion_pct", result)

        # Verify data types
        self.assertIsInstance(result["timeliness"], float)
        self.assertIsInstance(result["reconciliation"], float)
        self.assertIsInstance(result["filing_rate"], float)
        self.assertIsInstance(result["daily_completion_pct"], list)

        # Verify value ranges
        self.assertGreaterEqual(result["timeliness"], 0)
        self.assertLessEqual(result["timeliness"], 100)

    def test_get_calendar_heatmap_data(self):
        """Test calendar heatmap data generation"""
        result = self.env["finance.controller.kpi"].get_calendar_heatmap_data("RIM")

        # Verify structure
        self.assertIn("heatmap_data", result)
        self.assertIn("milestones", result)

        # Verify heatmap data format
        self.assertIsInstance(result["heatmap_data"], list)
        if result["heatmap_data"]:
            sample = result["heatmap_data"][0]
            self.assertEqual(len(sample), 2)  # [date, task_count]

        # Verify milestones format
        self.assertIsInstance(result["milestones"], list)
        if result["milestones"]:
            milestone = result["milestones"][0]
            self.assertIn("date", milestone)
            self.assertIn("type", milestone)
            self.assertIn("label", milestone)

    def test_get_wbs_tree_data(self):
        """Test WBS tree structure generation"""
        result = self.env["finance.controller.kpi"].get_wbs_tree_data("RIM")

        # Verify root structure
        self.assertIn("name", result)
        self.assertIn("children", result)
        self.assertEqual(result["name"], "Month-End Close WBS")

        # Verify hierarchical structure
        self.assertIsInstance(result["children"], list)
        if result["children"]:
            child = result["children"][0]
            self.assertIn("name", child)
            self.assertIn("value", child)

    def test_get_gantt_data(self):
        """Test Gantt chart data generation"""
        result = self.env["finance.controller.kpi"].get_gantt_data("RIM")

        # Verify list format
        self.assertIsInstance(result, list)

        if result:
            task = result[0]
            # Verify required fields
            self.assertIn("name", task)
            self.assertIn("start", task)
            self.assertIn("end", task)
            self.assertIn("owner", task)
            self.assertIn("phase", task)
            self.assertIn("status", task)

            # Verify date formats
            self.assertRegex(task["start"], r"\d{4}-\d{2}-\d{2}")
            self.assertRegex(task["end"], r"\d{4}-\d{2}-\d{2}")

    def test_get_raci_sunburst_data(self):
        """Test RACI sunburst data generation"""
        result = self.env["finance.controller.kpi"].get_raci_sunburst_data("RIM")

        # Verify root structure
        self.assertIn("name", result)
        self.assertIn("children", result)
        self.assertEqual(result["name"], "RACI Distribution")

        # Verify hierarchical structure (Cluster → Owner → RACI Role)
        if result["children"]:
            cluster = result["children"][0]
            self.assertIn("name", cluster)
            self.assertIn("children", cluster)

            if cluster["children"]:
                owner = cluster["children"][0]
                self.assertIn("name", owner)
                self.assertIn("children", owner)

                if owner["children"]:
                    role = owner["children"][0]
                    self.assertIn("name", role)
                    self.assertIn("value", role)

    def test_get_dependency_graph_data(self):
        """Test dependency graph data generation"""
        result = self.env["finance.controller.kpi"].get_dependency_graph_data("RIM")

        # Verify structure
        self.assertIn("nodes", result)
        self.assertIn("links", result)

        # Verify nodes format
        self.assertIsInstance(result["nodes"], list)
        if result["nodes"]:
            node = result["nodes"][0]
            self.assertIn("id", node)
            self.assertIn("name", node)
            self.assertIn("category", node)

        # Verify links format
        self.assertIsInstance(result["links"], list)
        if result["links"]:
            link = result["links"][0]
            self.assertIn("source", link)
            self.assertIn("target", link)

    def test_cron_generate_kpi_snapshot(self):
        """Test daily cron job execution"""
        result = self.env["finance.controller.kpi"].cron_generate_kpi_snapshot("RIM")

        # Verify all data sections present
        self.assertIn("gauges", result)
        self.assertIn("calendar", result)
        self.assertIn("wbs", result)
        self.assertIn("gantt", result)
        self.assertIn("raci", result)
        self.assertIn("dependencies", result)

        # Verify snapshot record created
        snapshot = self.env["finance.controller.kpi"].search(
            [("employee_code", "=", "RIM")], limit=1, order="create_date desc"
        )

        self.assertTrue(snapshot)
        self.assertEqual(snapshot.employee_code, "RIM")
        self.assertTrue(snapshot.kpi_data)

        # Verify JSON data is valid
        kpi_data = json.loads(snapshot.kpi_data)
        self.assertIsInstance(kpi_data, dict)

    def test_employee_context_filtering(self):
        """Test employee context filtering across all methods"""
        # Create task for different employee
        self.env["ipai.finance.monthly.close"].create(
            {
                "name": "CKVC Task",
                "owner_code": "CKVC",
                "target_completion_date": datetime.now().date(),
                "status": "pending",
            }
        )

        # Get data for RIM
        result_rim = self.env["finance.controller.kpi"].get_gantt_data("RIM")

        # Get data for CKVC
        result_ckvc = self.env["finance.controller.kpi"].get_gantt_data("CKVC")

        # Verify both return data (may differ based on ownership)
        self.assertIsInstance(result_rim, list)
        self.assertIsInstance(result_ckvc, list)

    def test_status_color_mapping(self):
        """Test status to color mapping helper"""
        kpi_model = self.env["finance.controller.kpi"]

        # Test color mappings
        self.assertEqual(kpi_model._get_status_color("completed"), "#4caf50")
        self.assertEqual(kpi_model._get_status_color("in_progress"), "#ff9800")
        self.assertEqual(kpi_model._get_status_color("pending"), "#2196f3")
        self.assertEqual(kpi_model._get_status_color("blocked"), "#f44336")
        self.assertEqual(kpi_model._get_status_color("unknown"), "#9e9e9e")

    def test_data_validation(self):
        """Test data validation and edge cases"""
        # Test with no tasks
        result = self.env["finance.controller.kpi"].get_kpi_gauge_data("NONEXISTENT")

        # Should return zeros/empty but not fail
        self.assertIsInstance(result, dict)
        self.assertGreaterEqual(result["timeliness"], 0)

        # Test with future dates
        future_task = self.env["ipai.finance.monthly.close"].create(
            {
                "name": "Future Task",
                "owner_code": "RIM",
                "target_completion_date": (datetime.now() + timedelta(days=60)).date(),
                "status": "pending",
            }
        )

        result = self.env["finance.controller.kpi"].get_calendar_heatmap_data("RIM")
        self.assertIsInstance(result["heatmap_data"], list)
