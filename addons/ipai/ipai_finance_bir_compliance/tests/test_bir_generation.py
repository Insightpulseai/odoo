# -*- coding: utf-8 -*-
"""Tests for ipai_finance_bir_compliance module."""
from datetime import date

from odoo.tests.common import TransactionCase


class TestBIRGeneration(TransactionCase):
    """Test BIR schedule loading and task generation."""

    def setUp(self):
        super().setUp()
        # Load program seed first
        from odoo.addons.ipai_project_program.seed.loader import (
            load_seed_bundle as load_program_seed,
        )

        load_program_seed(self.env, "ipai_project_program")

        # Load BIR schedule
        from odoo.addons.ipai_finance_bir_compliance.seed.loader import (
            load_seed_bundle as load_bir_seed,
        )

        load_bir_seed(self.env, "ipai_finance_bir_compliance")

    def test_schedule_loaded(self):
        """Test that BIR schedule items are loaded from seed."""
        Item = self.env["ipai.bir.schedule.item"]
        items = Item.search([])
        self.assertTrue(len(items) > 0)

        # Check specific item
        item = Item.search(
            [
                ("bir_form", "=", "1601-C / 0619-E"),
                ("period_covered", "=", "Dec 2025"),
            ],
            limit=1,
        )
        self.assertTrue(item)
        self.assertEqual(len(item.step_ids), 4)

    def test_generate_bir_tasks_idempotent(self):
        """Test that BIR task generation is idempotent."""
        prog = self.env.ref("ipai_project_program.prog_prj_2025_002")
        generator = self.env["ipai.bir.generator"]

        # First run should create tasks
        created1 = generator.generate(prog)
        self.assertTrue(created1 >= 1)

        # Second run should create 0 (idempotent)
        created2 = generator.generate(prog)
        self.assertEqual(created2, 0)

    def test_generate_with_date_filter(self):
        """Test generation with date range filter."""
        prog = self.env.ref("ipai_project_program.prog_prj_2025_002")
        generator = self.env["ipai.bir.generator"]

        # Only generate for January 2026
        created = generator.generate(
            prog,
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 31),
        )
        self.assertTrue(created > 0)

    def test_step_date_calculation(self):
        """Test step target date calculation."""
        Item = self.env["ipai.bir.schedule.item"]
        item = Item.search(
            [
                ("bir_form", "=", "1601-C / 0619-E"),
                ("period_covered", "=", "Dec 2025"),
            ],
            limit=1,
        )

        deadline = item.deadline  # 2026-01-15
        for step in item.step_ids:
            target = step.compute_target_date(deadline)
            # All targets should be on or before deadline
            self.assertLessEqual(target, deadline)
            # Filing step should be on deadline
            if step.activity_type == "file":
                self.assertEqual(target, deadline)

    def test_dry_run(self):
        """Test dry run mode."""
        prog = self.env.ref("ipai_project_program.prog_prj_2025_002")
        generator = self.env["ipai.bir.generator"]

        # Dry run should return count but not create
        count = generator.generate(prog, dry_run=True)
        self.assertTrue(count > 0)

        # Verify no tasks created
        im2 = self.env.ref("ipai_project_program.im2_tax_filing")
        tasks = self.env["project.task"].search(
            [
                ("project_id", "=", im2.id),
                ("bir_form", "!=", False),
            ]
        )
        self.assertEqual(len(tasks), 0)
