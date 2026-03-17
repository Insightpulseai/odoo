"""Tests for BIR VAT computation using rates data and rules engine."""

import csv
import json
import os
import unittest

_MODULE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_MODULE_PATH, "data")
_FIXTURES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


class TestBirVatCompute(unittest.TestCase):
    """Validate VAT rates and TRAIN law brackets from ph_rates_2025.json."""

    def setUp(self):
        rates_file = os.path.join(_DATA_PATH, "rates", "ph_rates_2025.json")
        with open(rates_file) as f:
            self.rates = json.load(f)

    def test_vat_standard_rate(self):
        """Standard VAT rate should be 12%."""
        self.assertEqual(self.rates["vat"]["standard_rate"], 0.12)

    def test_vat_zero_rated(self):
        """Zero-rated exports should be 0%."""
        self.assertEqual(self.rates["vat"]["zero_rated_exports"], 0.00)

    def test_vat_exempt(self):
        """VAT exempt rate should be 0%."""
        self.assertEqual(self.rates["vat"]["vat_exempt"], 0.00)

    def test_vat_registration_threshold(self):
        """VAT registration threshold should be PHP 3,000,000."""
        self.assertEqual(self.rates["vat"]["registration_threshold"], 3000000)

    def test_train_law_brackets_count(self):
        """TRAIN law should have 6 brackets."""
        brackets = self.rates["compensation_tax"]["ranges"]
        self.assertEqual(len(brackets), 6)

    def test_train_first_bracket_exempt(self):
        """First bracket is tax-exempt up to PHP 250,000."""
        bracket = self.rates["compensation_tax"]["ranges"][0]
        self.assertEqual(bracket["max"], 250000)
        self.assertEqual(bracket["rate"], 0.00)

    def test_train_second_bracket(self):
        """Second bracket: 15% on excess over PHP 250,000."""
        bracket = self.rates["compensation_tax"]["ranges"][1]
        self.assertEqual(bracket["min"], 250000)
        self.assertEqual(bracket["max"], 400000)
        self.assertEqual(bracket["rate"], 0.15)
        self.assertEqual(bracket["excess_over"], 250000)
        self.assertEqual(bracket["fixed_amount"], 0)

    def test_train_third_bracket(self):
        """Third bracket: PHP 22,500 + 20% on excess over PHP 400,000."""
        bracket = self.rates["compensation_tax"]["ranges"][2]
        self.assertEqual(bracket["min"], 400000)
        self.assertEqual(bracket["max"], 800000)
        self.assertEqual(bracket["rate"], 0.20)
        self.assertEqual(bracket["fixed_amount"], 22500)

    def test_train_top_bracket(self):
        """Top bracket: PHP 2,202,500 + 35% on excess over PHP 8,000,000."""
        bracket = self.rates["compensation_tax"]["ranges"][5]
        self.assertEqual(bracket["min"], 8000000)
        self.assertIsNone(bracket["max"])
        self.assertEqual(bracket["rate"], 0.35)
        self.assertEqual(bracket["fixed_amount"], 2202500)

    def test_train_bracket_continuity(self):
        """Each bracket's min equals the previous bracket's max."""
        brackets = self.rates["compensation_tax"]["ranges"]
        for i in range(1, len(brackets)):
            self.assertEqual(
                brackets[i]["min"],
                brackets[i - 1]["max"],
                msg=f"Gap between bracket {i - 1} and {i}",
            )

    def test_vat_computation_from_fixtures(self):
        """VAT computation on fixture transactions matches 12% rate."""
        txn_file = os.path.join(_FIXTURES_PATH, "vat_basic_transactions.csv")
        if not os.path.exists(txn_file):
            self.skipTest("Fixture file not found")

        with open(txn_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                gross = float(row.get("gross_amount", 0))
                tax_code = row.get("tax_code", "")

                if tax_code == "VAT_12_SALES" or tax_code == "VAT_12_PURCHASE":
                    expected_vat = gross * 0.12
                    computed_vat = gross * self.rates["vat"]["standard_rate"]
                    self.assertAlmostEqual(
                        expected_vat,
                        computed_vat,
                        places=2,
                        msg=f"VAT mismatch for {row.get('txn_id')}",
                    )

    def test_vat_metadata(self):
        """Rates metadata contains expected legal basis references."""
        metadata = self.rates["metadata"]
        self.assertEqual(metadata["source"], "Bureau of Internal Revenue (BIR)")
        legal_basis = metadata["legal_basis"]
        self.assertTrue(
            any("TRAIN" in lb for lb in legal_basis),
            "TRAIN Law should be referenced",
        )
        self.assertTrue(
            any("CREATE" in lb for lb in legal_basis),
            "CREATE Law should be referenced",
        )


if __name__ == "__main__":
    unittest.main()
