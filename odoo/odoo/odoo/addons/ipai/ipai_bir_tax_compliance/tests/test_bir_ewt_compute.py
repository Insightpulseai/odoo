"""Tests for BIR EWT computation using rates data and rules engine."""

import json
import os
import unittest

_MODULE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_MODULE_PATH, "data")


class TestBirEwtCompute(unittest.TestCase):
    """Validate EWT rates and corporate income tax from ph_rates_2025.json."""

    def setUp(self):
        rates_file = os.path.join(_DATA_PATH, "rates", "ph_rates_2025.json")
        with open(rates_file) as f:
            self.rates = json.load(f)

    def test_ewt_professional_fees_individual(self):
        """Professional fees (individuals) EWT should be 10%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["W010"]["rate"], 0.10
        )

    def test_ewt_professional_fees_juridical(self):
        """Professional fees (juridical) EWT should be 10%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["W020"]["rate"], 0.10
        )

    def test_ewt_professional_fees_medical(self):
        """Medical practitioners EWT should be 10%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["W030"]["rate"], 0.10
        )

    def test_ewt_professional_fees_lawyers(self):
        """Lawyers EWT should be 10%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["W040"]["rate"], 0.10
        )

    def test_ewt_supplier_goods(self):
        """Supplier goods EWT should be 1%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["W157"]["rate"], 0.01
        )

    def test_ewt_supplier_services(self):
        """Supplier services EWT should be 2%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["W158"]["rate"], 0.02
        )

    def test_ewt_commissions(self):
        """Commission agents EWT should be 10%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["W161"]["rate"], 0.10
        )

    def test_ewt_rent_real_property(self):
        """Rent (real property) EWT should be 5%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["W169"]["rate"], 0.05
        )

    def test_ewt_rent_personal_property(self):
        """Rent (personal property) EWT should be 5%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["W170"]["rate"], 0.05
        )

    def test_ewt_all_codes_have_rate(self):
        """Every EWT code has a numeric rate between 0 and 1."""
        for code, data in self.rates["expanded_withholding_tax"].items():
            rate = data.get("rate")
            self.assertIsNotNone(rate, f"Missing rate for {code}")
            self.assertGreaterEqual(rate, 0.0, f"Negative rate for {code}")
            self.assertLessEqual(rate, 1.0, f"Rate > 100% for {code}")

    def test_ewt_all_codes_have_base(self):
        """Every EWT code specifies a base (gross or other)."""
        for code, data in self.rates["expanded_withholding_tax"].items():
            self.assertIn(
                "base", data, f"Missing 'base' field for {code}"
            )

    def test_corporate_income_tax(self):
        """Corporate income tax should be 25% with 2% MCIT."""
        cit = self.rates["corporate_income_tax"]
        self.assertEqual(cit["standard_rate"], 0.25)
        self.assertEqual(cit["minimum_corporate_income_tax"], 0.02)

    def test_final_withholding_tax_interest(self):
        """Final withholding on bank interest should be 20%."""
        self.assertEqual(
            self.rates["final_withholding_tax"]["F001"]["rate"], 0.20
        )

    def test_final_withholding_tax_dividends(self):
        """Final withholding on cash dividends should be 10%."""
        self.assertEqual(
            self.rates["final_withholding_tax"]["F002"]["rate"], 0.10
        )

    def test_final_withholding_tax_royalties(self):
        """Final withholding on royalties should be 20%."""
        self.assertEqual(
            self.rates["final_withholding_tax"]["F004"]["rate"], 0.20
        )

    def test_ewt_computation_professional_10pct(self):
        """EWT on PHP 100,000 professional fees = PHP 10,000."""
        gross = 100000.0
        rate = self.rates["expanded_withholding_tax"]["W010"]["rate"]
        self.assertAlmostEqual(gross * rate, 10000.0, places=2)

    def test_ewt_computation_supplier_goods_1pct(self):
        """EWT on PHP 50,000 goods purchase = PHP 500."""
        gross = 50000.0
        rate = self.rates["expanded_withholding_tax"]["W157"]["rate"]
        self.assertAlmostEqual(gross * rate, 500.0, places=2)

    def test_ewt_computation_rent_5pct(self):
        """EWT on PHP 28,000 rent = PHP 1,400."""
        gross = 28000.0
        rate = self.rates["expanded_withholding_tax"]["W169"]["rate"]
        self.assertAlmostEqual(gross * rate, 1400.0, places=2)


if __name__ == "__main__":
    unittest.main()
