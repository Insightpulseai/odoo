from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestParityRecord(TransactionCase):
    """Tests for ipai.finance.gl.parity model."""

    def setUp(self):
        super().setUp()
        self.category = self.env["ipai.finance.gl.parity.category"].create(
            {
                "name": "Chart of Accounts",
                "code": "chart_of_accounts",
            }
        )

    def _make_parity(self, d365_concept, status, **kwargs):
        vals = {
            "d365_concept": d365_concept,
            "status": status,
            "category_id": self.category.id,
        }
        vals.update(kwargs)
        return self.env["ipai.finance.gl.parity"].create(vals)

    def test_01_create_gap_record_no_odoo_module(self):
        """A parity record with status='gap' does not require odoo_module."""
        rec = self._make_parity(
            "Main Account",
            "gap",
            d365_module="General Ledger",
            wave="Wave-01",
        )
        self.assertEqual(rec.status, "gap")
        self.assertFalse(rec.odoo_module)
        self.assertTrue(rec.id)

    def test_02_covered_without_odoo_module_raises(self):
        """status='covered' without odoo_module + odoo_model raises ValidationError."""
        with self.assertRaises(ValidationError):
            self._make_parity(
                "Chart of Accounts",
                "covered",
                d365_module="General Ledger",
                wave="Wave-01",
                # intentionally omitting odoo_module and odoo_model
            )

    def test_03_covered_with_odoo_module_and_model_succeeds(self):
        """status='covered' with odoo_module + odoo_model creates record successfully."""
        rec = self._make_parity(
            "Chart of Accounts",
            "covered",
            d365_module="General Ledger",
            wave="Wave-01",
            odoo_module="account",
            odoo_model="account.account",
        )
        self.assertEqual(rec.status, "covered")
        self.assertEqual(rec.odoo_module, "account")
        self.assertEqual(rec.odoo_model, "account.account")

    def test_04_name_compute_format(self):
        """Computed name returns '[GL] <d365_concept>' format."""
        rec = self._make_parity(
            "Chart of accounts",
            "gap",
            d365_module="General Ledger",
            wave="Wave-01",
        )
        self.assertEqual(rec.name, "[GL] Chart of accounts")

    def test_05_status_color_compute(self):
        """status_color returns the correct integer per status value."""
        expected_colors = {
            "covered": 10,
            "partial": 2,
            "gap": 1,
            "out_of_scope": 4,
        }
        for status, expected_color in expected_colors.items():
            extra = {}
            if status == "covered":
                extra = {"odoo_module": "account", "odoo_model": "account.account"}
            rec = self._make_parity(
                f"Concept for {status}",
                status,
                d365_module="General Ledger",
                wave=f"Wave-{status}",
                **extra,
            )
            self.assertEqual(
                rec.status_color,
                expected_color,
                msg=f"status_color mismatch for status='{status}'",
            )

    def test_06_unique_d365_concept_wave_constraint(self):
        """Creating two parity records with same (d365_concept, wave) raises."""
        self._make_parity(
            "Main Account",
            "gap",
            d365_module="General Ledger",
            wave="Wave-01",
        )
        with self.assertRaises(Exception):
            self._make_parity(
                "Main Account",
                "partial",
                d365_module="General Ledger",
                wave="Wave-01",
            )

    def test_07_action_open_odoo_model(self):
        """action_open_odoo_model returns an act_window dict when odoo_view_ref is set,
        and returns False or falsy when odoo_view_ref is not set."""
        # With odoo_view_ref set
        rec_with_ref = self._make_parity(
            "Account with view ref",
            "covered",
            d365_module="General Ledger",
            wave="Wave-02",
            odoo_module="account",
            odoo_model="account.account",
            odoo_view_ref="account.view_account_form",
        )
        action = rec_with_ref.action_open_odoo_model()
        self.assertIsInstance(action, dict)
        self.assertEqual(action.get("type"), "ir.actions.act_window")

        # Without odoo_view_ref set
        rec_no_ref = self._make_parity(
            "Account without view ref",
            "gap",
            d365_module="General Ledger",
            wave="Wave-03",
        )
        result = rec_no_ref.action_open_odoo_model()
        self.assertFalse(result)
