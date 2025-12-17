# -*- coding: utf-8 -*-
"""
Tests for the Month-End Close Task Generator.

These tests verify:
- Seed JSON loading and validation
- Idempotent task generation
- Completeness reporting
- Business day calculations
"""
import json
from datetime import date
from pathlib import Path

from odoo.tests.common import TransactionCase


class TestClosingGenerator(TransactionCase):
    """Test cases for ipai.close.generator"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Load seed JSON from file
        seed_file = (
            Path(__file__).parent.parent / "seed" / "closing_v1_2_0.json"
        )
        cls.seed = json.loads(seed_file.read_text())

    def test_seed_validation_passes(self):
        """Test that the bundled seed JSON passes validation."""
        Generator = self.env["ipai.close.generator"]

        # Should not raise
        Generator._validate_seed(self.seed)

        # Verify required keys present
        self.assertIn("schema_version", self.seed)
        self.assertIn("seed_id", self.seed)
        self.assertIn("timezone", self.seed)
        self.assertIn("directory", self.seed)
        self.assertIn("cycles", self.seed)

    def test_dry_run_returns_pass_status(self):
        """Test that a dry run with valid seed returns PASS or WARN status."""
        Generator = self.env["ipai.close.generator"]

        # Run in dry_run mode - should not create any records
        result = Generator.run(
            seed=self.seed,
            cycle_code="MONTH_END_CLOSE",
            cycle_key="MONTH_END_CLOSE|2025-12",
            dry_run=True,
        )

        # Should complete without errors
        self.assertIn("status", result)
        self.assertIn(result["status"], ["pass", "warn"])

        # Counts should be populated
        self.assertIn("counts", result)
        self.assertGreaterEqual(result["counts"]["created"], 0)

        # No tasks should actually be created in dry run
        # (verify by checking no generation run was committed)
        runs = self.env["ipai.close.generation.run"].search(
            [("cycle_key", "=", "MONTH_END_CLOSE|2025-12"), ("dry_run", "=", True)]
        )
        # Note: run record IS created even in dry_run for audit purposes
        self.assertTrue(runs)

    def test_flatten_templates(self):
        """Test template flattening from hierarchy."""
        Generator = self.env["ipai.close.generator"]
        cycle = Generator._find_cycle(self.seed, "MONTH_END_CLOSE")

        templates = Generator._flatten_templates(cycle)

        # Should have templates from all phases
        self.assertGreater(len(templates), 0)

        # Each template should have required fields
        for tpl in templates:
            self.assertIn("task_template_code", tpl)
            self.assertIn("name", tpl)
            self.assertIn("steps", tpl)
            self.assertGreater(len(tpl["steps"]), 0)

    def test_business_day_calculation(self):
        """Test business day calculations."""
        Generator = self.env["ipai.close.generator"]

        # Test November 2025 - last business day should be Friday Nov 28
        last_bd = Generator._get_last_business_day(2025, 11)
        self.assertEqual(last_bd, date(2025, 11, 28))
        self.assertEqual(last_bd.weekday(), 4)  # Friday

        # Test December 2025 - last business day should be Wednesday Dec 31
        last_bd_dec = Generator._get_last_business_day(2025, 12)
        self.assertEqual(last_bd_dec, date(2025, 12, 31))
        self.assertEqual(last_bd_dec.weekday(), 2)  # Wednesday

        # Test subtracting business days
        result = Generator._subtract_business_days(date(2025, 11, 28), 3)
        self.assertEqual(result, date(2025, 11, 25))  # Tuesday

    def test_idempotent_generation(self):
        """Test that running twice produces same result."""
        Generator = self.env["ipai.close.generator"]
        cycle_key = "MONTH_END_CLOSE|2025-12"

        # First run
        result1 = Generator.run(
            seed=self.seed,
            cycle_code="MONTH_END_CLOSE",
            cycle_key=cycle_key,
            dry_run=False,
        )

        created_first = result1["counts"]["created"]
        self.assertGreater(created_first, 0)

        # Second run - should update/unchanged, not create new
        result2 = Generator.run(
            seed=self.seed,
            cycle_code="MONTH_END_CLOSE",
            cycle_key=cycle_key,
            dry_run=False,
        )

        # No new tasks should be created
        self.assertEqual(result2["counts"]["created"], 0)
        # All should be unchanged (same hash)
        self.assertGreater(result2["counts"]["unchanged"], 0)

    def test_employee_code_fallback(self):
        """Test that unmapped employee codes don't fail generation."""
        Generator = self.env["ipai.close.generator"]

        # Create a modified seed with an unknown employee code
        modified_seed = json.loads(json.dumps(self.seed))
        cycle = next(
            c for c in modified_seed["cycles"]
            if c["cycle_code"] == "MONTH_END_CLOSE"
        )
        # Add a template with unknown assignee
        cycle["phases"][0]["workstreams"][0]["task_templates"].append({
            "task_template_code": "T_TEST_UNKNOWN_ASSIGNEE",
            "name": "Test Task with Unknown Assignee",
            "steps": [
                {"step_code": "PREP", "name": "Prep", "default_assignee": "UNKNOWN_CODE"}
            ],
            "dedupe_key": "MONTH_END_CLOSE|T_TEST_UNKNOWN_ASSIGNEE",
        })

        # Should complete with WARN status, not fail
        result = Generator.run(
            seed=modified_seed,
            cycle_code="MONTH_END_CLOSE",
            cycle_key="MONTH_END_CLOSE|2025-12",
            dry_run=True,
        )

        # Should have unresolved assignees but not fail
        self.assertIn(result["status"], ["pass", "warn"])
        # Unresolved assignees should be tracked
        self.assertGreater(len(result.get("unresolved_assignees", [])), 0)

    def test_project_creation(self):
        """Test that a project is created for the cycle."""
        Generator = self.env["ipai.close.generator"]
        Project = self.env["project.project"]

        # Run generator
        Generator.run(
            seed=self.seed,
            cycle_code="MONTH_END_CLOSE",
            cycle_key="MONTH_END_CLOSE|2025-11",
            dry_run=False,
        )

        # Project should exist
        project = Project.search([("x_cycle_code", "=", "MONTH_END_CLOSE")])
        self.assertTrue(project)
        self.assertEqual(project.name, "Month-End Closing")
