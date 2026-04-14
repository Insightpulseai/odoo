from odoo.exceptions import IntegrityError
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestParityCategory(TransactionCase):
    """Tests for ipai.finance.gl.parity.category model."""

    def _make_category(self, name, code, **kwargs):
        vals = {"name": name, "code": code}
        vals.update(kwargs)
        return self.env["ipai.finance.gl.parity.category"].create(vals)

    def test_01_create_category_defaults(self):
        """Creating a category applies default sequence=10 and active=True."""
        cat = self._make_category("Chart of Accounts", "chart_of_accounts")
        self.assertEqual(cat.sequence, 10)
        self.assertTrue(cat.active)
        self.assertEqual(cat.name, "Chart of Accounts")
        self.assertEqual(cat.code, "chart_of_accounts")

    def test_02_unique_code_constraint(self):
        """Creating two categories with the same code raises IntegrityError."""
        self._make_category("Chart of Accounts", "chart_of_accounts")
        with self.assertRaises((IntegrityError, Exception)):
            self._make_category("Chart of Accounts Duplicate", "chart_of_accounts")

    def test_03_archive_does_not_delete(self):
        """Archiving a category sets active=False but does not delete the record."""
        cat = self._make_category("Fiscal Calendar", "fiscal_calendar")
        cat_id = cat.id
        cat.write({"active": False})
        # Record must still exist when searched with active_test=False
        found = self.env["ipai.finance.gl.parity.category"].with_context(
            active_test=False
        ).search([("id", "=", cat_id)])
        self.assertTrue(found)
        self.assertFalse(found.active)

    def test_04_ordering_by_sequence_then_name(self):
        """Records are returned ordered by sequence, then name."""
        self._make_category("Zebra Category", "zebra", sequence=20)
        self._make_category("Alpha Category", "alpha", sequence=10)
        self._make_category("Beta Category", "beta", sequence=10)
        records = self.env["ipai.finance.gl.parity.category"].search(
            [("code", "in", ["zebra", "alpha", "beta"])]
        )
        # sequence 10 records come before sequence 20
        codes = records.mapped("code")
        self.assertIn("alpha", codes)
        self.assertIn("beta", codes)
        self.assertIn("zebra", codes)
        zebra_pos = codes.index("zebra")
        alpha_pos = codes.index("alpha")
        beta_pos = codes.index("beta")
        # Both alpha and beta (seq 10) must appear before zebra (seq 20)
        self.assertLess(alpha_pos, zebra_pos)
        self.assertLess(beta_pos, zebra_pos)
        # Within seq 10: alpha < beta alphabetically
        self.assertLess(alpha_pos, beta_pos)
