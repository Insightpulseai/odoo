from odoo.tests.common import TransactionCase
from odoo.tests import tagged


# Expected seed category codes, matching d365_parity_data.xml
_EXPECTED_SEED_CODES = [
    "chart_of_accounts",
    "fiscal_calendar",
    "financial_dimensions",
    "accounting_structure",
    "financial_journal",
    "periodic_process",
    "gl_overall",
]


@tagged("post_install", "-at_install")
class TestSeedData(TransactionCase):
    """Tests that the seed data from d365_parity_data.xml loaded correctly."""

    def test_01_seed_categories_count(self):
        """Exactly 7 seed categories exist after module installation."""
        categories = self.env["ipai.finance.gl.parity.category"].search(
            [("code", "in", _EXPECTED_SEED_CODES)]
        )
        self.assertEqual(
            len(categories),
            7,
            msg=(
                f"Expected 7 seed categories, found {len(categories)}. "
                f"Codes found: {categories.mapped('code')}"
            ),
        )

    def test_02_seed_categories_required_fields_populated(self):
        """Each seed category has name, code, and sequence populated."""
        categories = self.env["ipai.finance.gl.parity.category"].search(
            [("code", "in", _EXPECTED_SEED_CODES)]
        )
        self.assertEqual(len(categories), 7, "All 7 seed categories must be present")
        for cat in categories:
            self.assertTrue(
                cat.name,
                msg=f"Category with code='{cat.code}' is missing a name",
            )
            self.assertTrue(
                cat.code,
                msg=f"Category id={cat.id} is missing a code",
            )
            self.assertIsInstance(
                cat.sequence,
                int,
                msg=f"Category code='{cat.code}' sequence must be an integer",
            )
            self.assertGreater(
                cat.sequence,
                0,
                msg=f"Category code='{cat.code}' sequence must be > 0",
            )
