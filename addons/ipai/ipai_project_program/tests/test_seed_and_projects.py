# -*- coding: utf-8 -*-
"""Tests for ipai_project_program module."""
from odoo.tests.common import TransactionCase


class TestSeedAndProjects(TransactionCase):
    """Test seed loading and project hierarchy."""

    def setUp(self):
        super().setUp()
        # Import and run seed loader
        from odoo.addons.ipai_project_program.seed.loader import load_seed_bundle
        load_seed_bundle(self.env, module_name="ipai_project_program")

    def test_seed_idempotent(self):
        """Test that seed loading is idempotent."""
        from odoo.addons.ipai_project_program.seed.loader import load_seed_bundle

        # Run seed again - should not create duplicates
        load_seed_bundle(self.env, module_name="ipai_project_program")
        load_seed_bundle(self.env, module_name="ipai_project_program")

        # Verify program exists
        prog = self.env.ref("ipai_project_program.prog_prj_2025_002")
        self.assertTrue(prog)
        self.assertTrue(prog.is_program)
        self.assertEqual(prog.program_code, "PRJ-2025-002")

        # Verify IMs exist
        im1 = self.env.ref("ipai_project_program.im1_month_end_closing")
        im2 = self.env.ref("ipai_project_program.im2_tax_filing")
        self.assertEqual(im1.parent_id.id, prog.id)
        self.assertEqual(im2.parent_id.id, prog.id)
        self.assertEqual(im1.im_code, "IM1")
        self.assertEqual(im2.im_code, "IM2")

    def test_directory_loaded(self):
        """Test that directory people are loaded."""
        d = self.env["ipai.directory.person"].search([("code", "=", "CKVC")], limit=1)
        self.assertTrue(d)
        self.assertEqual(d.name, "Khalil Veracruz")
        self.assertEqual(d.role, "Finance Director")

    def test_stages_loaded(self):
        """Test that task stages are loaded."""
        Stage = self.env["project.task.type"]
        prep = Stage.search([("name", "=", "Preparation")], limit=1)
        review = Stage.search([("name", "=", "Review")], limit=1)
        approval = Stage.search([("name", "=", "Approval")], limit=1)
        filed = Stage.search([("name", "=", "Filed")], limit=1)

        self.assertTrue(prep)
        self.assertTrue(review)
        self.assertTrue(approval)
        self.assertTrue(filed)

    def test_program_rollups(self):
        """Test program roll-up computed fields."""
        prog = self.env.ref("ipai_project_program.prog_prj_2025_002")
        self.assertEqual(prog.im_count, 2)
        # No tasks yet, so im_task_count should be 0
        self.assertEqual(prog.im_task_count, 0)

    def test_convert_phases_wizard(self):
        """Test the convert phases wizard."""
        # Create a fresh program
        prog = self.env["project.project"].create({
            "name": "Test Program",
            "is_program": True,
            "program_code": "TEST-001",
        })

        # Create wizard
        wizard = self.env["ipai.convert.phases.wizard"].create({
            "parent_project_id": prog.id,
            "im1_name": "Test IM1",
            "im2_name": "Test IM2",
            "move_tasks_by_keyword": False,
        })

        # Run conversion
        wizard.action_convert()

        # Verify IMs created
        im1 = self.env["project.project"].search([
            ("parent_id", "=", prog.id),
            ("im_code", "=", "IM1"),
        ], limit=1)
        im2 = self.env["project.project"].search([
            ("parent_id", "=", prog.id),
            ("im_code", "=", "IM2"),
        ], limit=1)

        self.assertTrue(im1)
        self.assertTrue(im2)
        self.assertEqual(im1.name, "Test IM1")
        self.assertEqual(im2.name, "Test IM2")
