from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestBirTaxCompliance(TransactionCase):
    """Tests for Philippine BIR withholding tax computation and contribution tables."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TaxTable = cls.env["ipai.bir.tax.table"]
        cls.TaxBracket = cls.env["ipai.bir.tax.bracket"]
        cls.ContribTable = cls.env["ipai.bir.contribution.table"]
        cls.ContribLine = cls.env["ipai.bir.contribution.line"]

        # Create a monthly withholding tax table mirroring 2023 TRAIN law
        cls.tax_table = cls.TaxTable.create(
            {
                "name": "Test Monthly WHT 2023",
                "table_type": "monthly",
                "effective_date": "2023-01-01",
            }
        )

        # Bracket data: (range_from, range_to, base_tax, excess_rate, excess_over)
        brackets = [
            (0, 20833, 0, 0, 0),
            (20833, 33333, 0, 0.15, 20833),
            (33333, 66667, 1875, 0.20, 33333),
            (66667, 166667, 8541.80, 0.25, 66667),
            (166667, 666667, 33541.80, 0.30, 166667),
            (666667, 0, 183541.80, 0.35, 666667),
        ]
        for rf, rt, bt, er, eo in brackets:
            cls.TaxBracket.create(
                {
                    "table_id": cls.tax_table.id,
                    "range_from": rf,
                    "range_to": rt,
                    "base_tax": bt,
                    "excess_rate": er,
                    "excess_over": eo,
                }
            )

    # ------------------------------------------------------------------
    # Withholding tax computation tests
    # ------------------------------------------------------------------

    def test_zero_tax_bracket(self):
        """Income <= 20,833 should yield zero withholding tax."""
        self.assertAlmostEqual(self.tax_table.compute_withholding(15000), 0.0, places=2)
        self.assertAlmostEqual(self.tax_table.compute_withholding(20833), 0.0, places=2)

    def test_bracket_2_known_value(self):
        """25,000 PHP: 0 + 15% * (25000 - 20833) = 625.05"""
        result = self.tax_table.compute_withholding(25000)
        expected = 0 + 0.15 * (25000 - 20833)  # 625.05
        self.assertAlmostEqual(result, expected, places=2)

    def test_bracket_3_known_value(self):
        """50,000 PHP: 1875 + 20% * (50000 - 33333) = 1875 + 3333.40 = 5208.40"""
        result = self.tax_table.compute_withholding(50000)
        expected = 1875 + 0.20 * (50000 - 33333)  # 5208.40
        self.assertAlmostEqual(result, expected, places=2)

    def test_bracket_4_known_value(self):
        """100,000 PHP: 8541.80 + 25% * (100000 - 66667) = 8541.80 + 8333.25 = 16875.05"""
        result = self.tax_table.compute_withholding(100000)
        expected = 8541.80 + 0.25 * (100000 - 66667)  # 16875.05
        self.assertAlmostEqual(result, expected, places=2)

    def test_bracket_5_known_value(self):
        """300,000 PHP: 33541.80 + 30% * (300000 - 166667) = 33541.80 + 39999.90 = 73541.70"""
        result = self.tax_table.compute_withholding(300000)
        expected = 33541.80 + 0.30 * (300000 - 166667)  # 73541.70
        self.assertAlmostEqual(result, expected, places=2)

    def test_top_bracket(self):
        """1,000,000 PHP: 183541.80 + 35% * (1000000 - 666667) = 183541.80 + 116666.55 = 300208.35"""
        result = self.tax_table.compute_withholding(1000000)
        expected = 183541.80 + 0.35 * (1000000 - 666667)  # 300208.35
        self.assertAlmostEqual(result, expected, places=2)

    def test_zero_income(self):
        """Zero or negative income should return 0."""
        self.assertAlmostEqual(self.tax_table.compute_withholding(0), 0.0, places=2)
        self.assertAlmostEqual(self.tax_table.compute_withholding(-5000), 0.0, places=2)

    def test_boundary_values(self):
        """Exact bracket boundary values should compute correctly."""
        # Exactly 33,333 is the boundary between bracket 2 and 3
        result = self.tax_table.compute_withholding(33333)
        # Falls in bracket 2: 0 + 15% * (33333 - 20833) = 1875.00
        expected = 0 + 0.15 * (33333 - 20833)
        self.assertAlmostEqual(result, expected, places=2)

    # ------------------------------------------------------------------
    # Contribution table CRUD tests
    # ------------------------------------------------------------------

    def test_contribution_table_create(self):
        """Create an SSS contribution table with lines."""
        table = self.ContribTable.create(
            {
                "name": "SSS Contribution Table 2023",
                "contribution_type": "sss",
                "effective_date": "2023-01-01",
            }
        )
        self.assertEqual(table.contribution_type, "sss")
        self.assertTrue(table.active)

        line = self.ContribLine.create(
            {
                "table_id": table.id,
                "range_from": 4000,
                "range_to": 4249.99,
                "employee_share": 180,
                "employer_share": 380,
            }
        )
        self.assertEqual(line.employee_share, 180)
        self.assertEqual(line.employer_share, 380)
        self.assertEqual(len(table.line_ids), 1)

    def test_contribution_table_philhealth(self):
        """Create a PhilHealth contribution table."""
        table = self.ContribTable.create(
            {
                "name": "PhilHealth 2023",
                "contribution_type": "philhealth",
                "effective_date": "2023-01-01",
            }
        )
        self.assertEqual(table.contribution_type, "philhealth")

    def test_contribution_table_pagibig(self):
        """Create a Pag-IBIG contribution table."""
        table = self.ContribTable.create(
            {
                "name": "Pag-IBIG 2023",
                "contribution_type": "pagibig",
                "effective_date": "2023-01-01",
            }
        )
        self.assertEqual(table.contribution_type, "pagibig")

    def test_contribution_line_cascade_delete(self):
        """Deleting a contribution table cascades to its lines."""
        table = self.ContribTable.create(
            {
                "name": "Cascade Test",
                "contribution_type": "sss",
                "effective_date": "2023-01-01",
            }
        )
        line = self.ContribLine.create(
            {
                "table_id": table.id,
                "range_from": 1000,
                "range_to": 1999.99,
                "employee_share": 50,
                "employer_share": 100,
            }
        )
        line_id = line.id
        table.unlink()
        self.assertFalse(self.ContribLine.search([("id", "=", line_id)]))

    def test_tax_bracket_cascade_delete(self):
        """Deleting a tax table cascades to its brackets."""
        table = self.TaxTable.create(
            {
                "name": "Cascade Test Tax",
                "table_type": "monthly",
                "effective_date": "2023-06-01",
            }
        )
        bracket = self.TaxBracket.create(
            {
                "table_id": table.id,
                "range_from": 0,
                "range_to": 10000,
                "base_tax": 0,
                "excess_rate": 0,
                "excess_over": 0,
            }
        )
        bracket_id = bracket.id
        table.unlink()
        self.assertFalse(self.TaxBracket.search([("id", "=", bracket_id)]))
