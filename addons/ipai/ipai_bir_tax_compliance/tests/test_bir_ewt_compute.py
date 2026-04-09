"""Tests for BIR EWT computation using rates data and rules engine.

ATC codes use BIR official format per RR 11-2018 Annex (WI/WC/WB prefix).
"""

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

    # --- EWT Professional Fees ---

    def test_ewt_professional_fees_individual_vat(self):
        """Professional fees (individuals, VAT or >3M) EWT should be 10%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WI010"]["rate"], 0.10
        )

    def test_ewt_professional_fees_individual_nonvat(self):
        """Professional fees (individuals, non-VAT ≤3M) EWT should be 5%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WI011"]["rate"], 0.05
        )

    def test_ewt_professional_fees_juridical(self):
        """Professional fees (juridical) EWT should be 10%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WI020"]["rate"], 0.10
        )

    def test_ewt_professional_fees_medical(self):
        """Medical practitioners EWT should be 10%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WI030"]["rate"], 0.10
        )

    def test_ewt_bookkeeping_individual(self):
        """Bookkeeping agents (individuals) EWT should be 10%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WI040"]["rate"], 0.10
        )

    # --- EWT Contractor Payments ---

    def test_ewt_contractor_individual(self):
        """Contractor (individual) EWT should be 2%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WC010"]["rate"], 0.02
        )

    def test_ewt_contractor_juridical(self):
        """Contractor (juridical) EWT should be 2%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WC020"]["rate"], 0.02
        )

    # --- EWT Government Payments ---

    def test_ewt_govt_goods(self):
        """Government procurement of goods EWT should be 1%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WC600"]["rate"], 0.01
        )

    def test_ewt_govt_services(self):
        """Government procurement of services EWT should be 2%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WC610"]["rate"], 0.02
        )

    # --- EWT Commissions ---

    def test_ewt_commissions_individual(self):
        """Commissions (individuals) EWT should be 10%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WC100"]["rate"], 0.10
        )

    # --- EWT Rent ---

    def test_ewt_rent_real_property_individual(self):
        """Rent (real property, individuals) EWT should be 5%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WB010"]["rate"], 0.05
        )

    def test_ewt_rent_real_property_juridical(self):
        """Rent (real property, juridical) EWT should be 5%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WB020"]["rate"], 0.05
        )

    def test_ewt_rent_personal_property(self):
        """Rent (personal property) EWT should be 5%."""
        self.assertEqual(
            self.rates["expanded_withholding_tax"]["WB050"]["rate"], 0.05
        )

    # --- Structural Validation ---

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

    def test_ewt_codes_use_official_format(self):
        """All EWT codes use BIR official WI/WC/WB prefix format."""
        for code in self.rates["expanded_withholding_tax"]:
            self.assertRegex(
                code, r'^W[ICB]\d{3}',
                f"ATC code {code} does not match BIR official format (WI/WC/WB + 3 digits)"
            )

    # --- Corporate Income Tax ---

    def test_corporate_income_tax_standard(self):
        """Standard CIT should be 25% (CREATE Law)."""
        cit = self.rates["corporate_income_tax"]
        self.assertEqual(cit["standard_rate"], 0.25)

    def test_corporate_income_tax_sme(self):
        """SME CIT should be 20% (CREATE Law)."""
        cit = self.rates["corporate_income_tax"]
        self.assertEqual(cit["sme_rate"], 0.20)

    def test_corporate_income_tax_mcit(self):
        """MCIT should be 1% (CREATE MORE, RA 12066 — permanent)."""
        cit = self.rates["corporate_income_tax"]
        self.assertEqual(cit["minimum_corporate_income_tax"], 0.01)

    # --- Final Withholding Tax (Resident) ---

    def test_fwt_interest_deposits(self):
        """FWT on bank interest should be 20%."""
        self.assertEqual(
            self.rates["final_withholding_tax"]["resident"]["F001"]["rate"], 0.20
        )

    def test_fwt_dividends_individual(self):
        """FWT on cash dividends (individuals) should be 10%."""
        self.assertEqual(
            self.rates["final_withholding_tax"]["resident"]["F002"]["rate"], 0.10
        )

    def test_fwt_royalties_general(self):
        """FWT on royalties (general) should be 20%."""
        self.assertEqual(
            self.rates["final_withholding_tax"]["resident"]["F004"]["rate"], 0.20
        )

    def test_fwt_royalties_literary(self):
        """FWT on royalties (books/literary) should be 10%."""
        self.assertEqual(
            self.rates["final_withholding_tax"]["resident"]["F004A"]["rate"], 0.10
        )

    # --- Final Withholding Tax (Non-Resident) ---

    def test_fwt_nrfc_general(self):
        """NRFC general income FWT should be 25% (CREATE, reduced from 30%)."""
        self.assertEqual(
            self.rates["final_withholding_tax"]["non_resident"]["NR001"]["rate"], 0.25
        )

    def test_fwt_nrfc_interest(self):
        """NRFC interest FWT should be 20%."""
        self.assertEqual(
            self.rates["final_withholding_tax"]["non_resident"]["NR003"]["rate"], 0.20
        )

    # --- Percentage Tax ---

    def test_percentage_tax_rate(self):
        """Percentage tax should be 3% (temporary 1% expired)."""
        self.assertEqual(
            self.rates["percentage_tax"]["standard_rate"], 0.03
        )

    # --- VAT ---

    def test_vat_standard_rate(self):
        """Standard VAT should be 12%."""
        self.assertEqual(self.rates["vat"]["standard_rate"], 0.12)

    def test_vat_digital_services(self):
        """Digital services VAT should be 12% (RA 12023)."""
        self.assertEqual(self.rates["vat"]["digital_services_rate"], 0.12)

    def test_vat_registration_threshold(self):
        """VAT registration threshold should be PHP 3,000,000."""
        self.assertEqual(self.rates["vat"]["registration_threshold"], 3000000)

    # --- Computation Tests ---

    def test_ewt_computation_professional_10pct(self):
        """EWT on PHP 100,000 professional fees (VAT) = PHP 10,000."""
        gross = 100000.0
        rate = self.rates["expanded_withholding_tax"]["WI010"]["rate"]
        self.assertAlmostEqual(gross * rate, 10000.0, places=2)

    def test_ewt_computation_professional_5pct(self):
        """EWT on PHP 100,000 professional fees (non-VAT) = PHP 5,000."""
        gross = 100000.0
        rate = self.rates["expanded_withholding_tax"]["WI011"]["rate"]
        self.assertAlmostEqual(gross * rate, 5000.0, places=2)

    def test_ewt_computation_contractor_2pct(self):
        """EWT on PHP 50,000 contractor payment = PHP 1,000."""
        gross = 50000.0
        rate = self.rates["expanded_withholding_tax"]["WC010"]["rate"]
        self.assertAlmostEqual(gross * rate, 1000.0, places=2)

    def test_ewt_computation_govt_goods_1pct(self):
        """EWT on PHP 50,000 government goods = PHP 500."""
        gross = 50000.0
        rate = self.rates["expanded_withholding_tax"]["WC600"]["rate"]
        self.assertAlmostEqual(gross * rate, 500.0, places=2)

    def test_ewt_computation_rent_5pct(self):
        """EWT on PHP 28,000 rent = PHP 1,400."""
        gross = 28000.0
        rate = self.rates["expanded_withholding_tax"]["WB010"]["rate"]
        self.assertAlmostEqual(gross * rate, 1400.0, places=2)

    # --- Metadata ---

    def test_metadata_version(self):
        """Rate file version should be 2025.2."""
        self.assertEqual(self.rates["metadata"]["version"], "2025.2")

    def test_metadata_includes_create_more(self):
        """Legal basis must include CREATE MORE Act (RA 12066)."""
        legal_basis = self.rates["metadata"]["legal_basis"]
        create_more_found = any("12066" in basis or "CREATE MORE" in basis for basis in legal_basis)
        self.assertTrue(create_more_found, "CREATE MORE Act (RA 12066) missing from legal_basis")

    def test_metadata_includes_digital_vat(self):
        """Legal basis must include VAT on Digital Services Act (RA 12023)."""
        legal_basis = self.rates["metadata"]["legal_basis"]
        digital_vat_found = any("12023" in basis for basis in legal_basis)
        self.assertTrue(digital_vat_found, "RA 12023 (Digital Services VAT) missing from legal_basis")


if __name__ == "__main__":
    unittest.main()
