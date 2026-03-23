from odoo.tests.common import TransactionCase


class TestFinancePPMSmoke(TransactionCase):
    """Smoke tests for ipai_finance_ppm module seed."""

    def test_project_ppm_fields_exist(self):
        """PPM fields are present on project.project after install."""
        Project = self.env["project.project"]
        field_names = Project._fields.keys()
        self.assertIn("ipai_ppm_budget_amount", field_names)
        self.assertIn("ipai_ppm_cost_center", field_names)
        self.assertIn("ipai_ppm_import_batch_id", field_names)
        self.assertIn("ipai_ppm_imported_at", field_names)
        self.assertIn("ipai_ppm_import_source", field_names)

    def test_analytic_ppm_fields_exist(self):
        """PPM fields are present on account.analytic.account after install."""
        AA = self.env["account.analytic.account"]
        field_names = AA._fields.keys()
        self.assertIn("ipai_ppm_budget_amount", field_names)
        self.assertIn("ipai_ppm_budget_source_project_id", field_names)
        self.assertIn("ipai_ppm_import_batch_id", field_names)

    def test_import_wizard_model_exists(self):
        """PPM import wizard transient model is registered."""
        Wizard = self.env["ipai.ppm.import.wizard"]
        self.assertTrue(Wizard)
        field_names = Wizard._fields.keys()
        self.assertIn("file", field_names)
        self.assertIn("batch_id", field_names)

    def test_budget_sync_method(self):
        """Budget sync from project to analytic account works."""
        plan = self.env["account.analytic.plan"].create({"name": "PPM Test Plan"})
        aa = self.env["account.analytic.account"].create({
            "name": "Test PPM Analytic",
            "plan_id": plan.id,
        })
        project = self.env["project.project"].create({
            "name": "Test PPM Project",
            "analytic_account_id": aa.id,
            "ipai_ppm_budget_amount": 50000.0,
            "ipai_ppm_cost_center": "CC-100",
        })
        result = self.env["account.analytic.account"].ipai_sync_project_budget_to_analytic(project.id)
        self.assertTrue(result)
        self.assertEqual(aa.ipai_ppm_budget_amount, 50000.0)
        self.assertEqual(aa.ipai_ppm_budget_source_project_id, project)

    def test_import_provenance(self):
        """Import provenance stamps are applied correctly."""
        project = self.env["project.project"].create({"name": "Provenance Test"})
        project.ipai_apply_import_provenance([project.id], "BATCH001", "csv")
        self.assertEqual(project.ipai_ppm_import_batch_id, "BATCH001")
        self.assertEqual(project.ipai_ppm_import_source, "csv")
        self.assertTrue(project.ipai_ppm_imported_at)

    def test_okr_dashboard_action_exists(self):
        """OKR dashboard client action is registered."""
        action = self.env.ref(
            "ipai_finance_ppm.action_finance_ppm_okr_dashboard",
            raise_if_not_found=False,
        )
        self.assertTrue(action)
        self.assertEqual(action.tag, "finance_ppm.okr_dashboard")

    def test_cron_exists(self):
        """Budget sync cron job is registered and active."""
        cron = self.env.ref(
            "ipai_finance_ppm.ir_cron_ipai_ppm_sync_budgets",
            raise_if_not_found=False,
        )
        self.assertTrue(cron)
        self.assertTrue(cron.active)
