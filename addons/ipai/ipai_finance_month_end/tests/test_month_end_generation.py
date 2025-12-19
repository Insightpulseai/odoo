# -*- coding: utf-8 -*-
"""Tests for ipai_finance_month_end module."""
from datetime import date
from odoo.tests.common import TransactionCase


class TestMonthEndGeneration(TransactionCase):
    """Test month-end template loading and task generation."""

    def setUp(self):
        super().setUp()
        # Load program seed first
        from odoo.addons.ipai_project_program.seed.loader import load_seed_bundle as load_program_seed
        load_program_seed(self.env, "ipai_project_program")

        # Load month-end templates
        from odoo.addons.ipai_finance_month_end.seed.loader import load_seed_bundle as load_month_end_seed
        load_month_end_seed(self.env, "ipai_finance_month_end")

    def test_templates_loaded(self):
        """Test that templates are loaded from seed."""
        Template = self.env["ipai.month.end.template"]
        templates = Template.search([])
        self.assertTrue(len(templates) > 0)

        # Check specific template
        payroll = Template.search([("task_base_name", "=", "Payroll Processing")], limit=1)
        self.assertTrue(payroll)
        self.assertEqual(payroll.category, "Payroll & Personnel")
        self.assertEqual(len(payroll.step_ids), 3)

    def test_generate_tasks_idempotent(self):
        """Test that task generation is idempotent."""
        prog = self.env.ref("ipai_project_program.prog_prj_2025_002")
        generator = self.env["ipai.month.end.generator"]

        # Use end of month as anchor
        anchor = date(2025, 12, 31)

        # First run should create tasks
        created1 = generator.generate(prog, anchor)
        self.assertTrue(created1 >= 1)

        # Second run should create 0 (idempotent)
        created2 = generator.generate(prog, anchor)
        self.assertEqual(created2, 0)

    def test_dry_run(self):
        """Test dry run mode."""
        prog = self.env.ref("ipai_project_program.prog_prj_2025_002")
        generator = self.env["ipai.month.end.generator"]
        anchor = date(2025, 11, 30)

        # Dry run should return count but not create
        count = generator.generate(prog, anchor, dry_run=True)
        self.assertTrue(count > 0)

        # Verify no tasks created
        im1 = self.env.ref("ipai_project_program.im1_month_end_closing")
        tasks = self.env["project.task"].search([
            ("project_id", "=", im1.id),
            ("date_deadline", "<=", anchor),
        ])
        self.assertEqual(len(tasks), 0)

    def test_step_date_calculation(self):
        """Test step target date calculation."""
        Template = self.env["ipai.month.end.template"]
        payroll = Template.search([("task_base_name", "=", "Payroll Processing")], limit=1)

        anchor = date(2025, 12, 31)  # Wednesday
        for step in payroll.step_ids:
            target = step.compute_target_date(anchor)
            # All targets should be before or on anchor
            self.assertLessEqual(target, anchor)
