# -*- coding: utf-8 -*-
"""Offline tests for the deterministic PH invoice math validator.

These tests do NOT require Odoo — they validate pure arithmetic logic
using the Dataverse/TBWA invoice fixture.
"""
import unittest
from copy import deepcopy

import sys
import os

# Allow standalone execution without Odoo
_validators_dir = os.path.join(
    os.path.dirname(__file__), os.pardir, "validators",
)
sys.path.insert(0, os.path.abspath(_validators_dir))
from ph_invoice_math import validate


# ------------------------------------------------------------------
# Fixture: real Dataverse/TBWA invoice that the LLM incorrectly
# said was "all correct".
# ------------------------------------------------------------------
_FIXTURE_INVOICE = {
    "lines": [
        {
            "description": "Professional Services — March 2026",
            "qty": 1,
            "unit_cost": 86734.69,
            "amount": 86734.69,
        },
    ],
    "net_of_vat": 86734.69,
    "vat_rate": 0.12,
    "vat_amount": 10408.16,
    "gross_total": 97142.85,
    "withholding_rate": 0.02,
    "withholding_amount": 1734.69,
    "printed_total_due": 85000.00,
}


class TestPhInvoiceMath(unittest.TestCase):
    """Deterministic PH invoice math validation tests."""

    def test_invoice_flags_printed_total_due_mismatch(self):
        """The real invoice prints 85,000 but expected payable is 95,408.16.

        Delta is exactly the VAT amount — the printed total treats
        net cash excluding VAT, which is incorrect for a VAT-inclusive
        invoice.  The validator MUST catch this.
        """
        result = validate(_FIXTURE_INVOICE)

        self.assertEqual(result["status"], "needs_review")
        self.assertEqual(result["expected_payable"], "95408.16")
        self.assertEqual(result["printed_total_due"], "85000.00")

        codes = [f["code"] for f in result["findings"]]
        self.assertIn("PRINTED_TOTAL_DUE_MISMATCH", codes)

        # Verify delta on the finding
        mismatch = next(
            f for f in result["findings"]
            if f["code"] == "PRINTED_TOTAL_DUE_MISMATCH"
        )
        self.assertEqual(mismatch["expected"], "95408.16")
        self.assertEqual(mismatch["actual"], "85000.00")
        self.assertEqual(mismatch["delta"], "10408.16")
        self.assertEqual(mismatch["severity"], "error")

    def test_corrected_invoice_passes(self):
        """Same invoice but with the correct printed_total_due."""
        doc = deepcopy(_FIXTURE_INVOICE)
        doc["printed_total_due"] = 95408.16

        result = validate(doc)

        self.assertEqual(result["status"], "validated")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["expected_payable"], "95408.16")

    def test_vat_mismatch(self):
        """Tweak vat_amount to a wrong value — validator must flag it."""
        doc = deepcopy(_FIXTURE_INVOICE)
        doc["vat_amount"] = 9999.99
        # Adjust gross_total to keep other checks from also firing
        doc["gross_total"] = doc["net_of_vat"] + 9999.99

        result = validate(doc)

        self.assertEqual(result["status"], "needs_review")
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("VAT_MISMATCH", codes)

        vat_finding = next(
            f for f in result["findings"] if f["code"] == "VAT_MISMATCH"
        )
        self.assertEqual(vat_finding["expected"], "10408.16")
        self.assertEqual(vat_finding["actual"], "9999.99")
        self.assertEqual(vat_finding["severity"], "error")

    def test_line_sum_mismatch(self):
        """Line qty * unit_cost != reported line amount."""
        doc = deepcopy(_FIXTURE_INVOICE)
        doc["lines"][0]["amount"] = 80000.00  # wrong

        result = validate(doc)

        codes = [f["code"] for f in result["findings"]]
        self.assertIn("LINE_SUM_MISMATCH", codes)

    def test_withholding_mismatch(self):
        """Wrong withholding amount flagged."""
        doc = deepcopy(_FIXTURE_INVOICE)
        doc["withholding_amount"] = 5000.00

        result = validate(doc)

        codes = [f["code"] for f in result["findings"]]
        self.assertIn("WITHHOLDING_MISMATCH", codes)

    def test_gross_total_mismatch(self):
        """Wrong gross total flagged."""
        doc = deepcopy(_FIXTURE_INVOICE)
        doc["gross_total"] = 100000.00

        result = validate(doc)

        codes = [f["code"] for f in result["findings"]]
        self.assertIn("GROSS_TOTAL_MISMATCH", codes)

    def test_no_lines_skips_line_check(self):
        """When no lines are provided, skip the line sum check."""
        doc = deepcopy(_FIXTURE_INVOICE)
        doc.pop("lines")
        doc["printed_total_due"] = 95408.16

        result = validate(doc)

        codes = [f["code"] for f in result["findings"]]
        self.assertNotIn("LINE_SUM_MISMATCH", codes)

    def test_default_rates(self):
        """Omitting vat_rate and withholding_rate uses PH defaults."""
        doc = deepcopy(_FIXTURE_INVOICE)
        doc.pop("vat_rate")
        doc.pop("withholding_rate")
        doc["printed_total_due"] = 95408.16

        result = validate(doc)

        self.assertEqual(result["status"], "validated")


if __name__ == "__main__":
    unittest.main()
