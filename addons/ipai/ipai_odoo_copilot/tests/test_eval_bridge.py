# -*- coding: utf-8 -*-
"""Bridge tests: BIR eval dataset scenarios → ph_invoice_math validator.

Constructs invoice documents from BIR tax eval CSV scenarios and validates
them through the deterministic ph_invoice_math validator.  Runs standalone
without Odoo.

Coverage:
  - VAT output scenarios → validator checks VAT_MISMATCH, GROSS_TOTAL
  - EWT scenarios → validator checks WITHHOLDING_MISMATCH
  - Combined VAT+EWT → full invoice with all 5 checks
"""

import csv
import json
import os
import sys
import unittest
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP

# Allow standalone execution without Odoo
_MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_VALIDATORS_DIR = os.path.join(_MODULE_DIR, "validators")
sys.path.insert(0, os.path.abspath(_VALIDATORS_DIR))
from ph_invoice_math import validate  # noqa: E402

# BIR tax compliance module paths
_BIR_MODULE = os.path.join(
    os.path.dirname(_MODULE_DIR), "ipai_bir_tax_compliance",
)
_BIR_RATES = os.path.join(_BIR_MODULE, "data", "rates", "ph_rates_2025.json")
_BIR_EVAL_CSV = os.path.join(
    _BIR_MODULE, "tests", "fixtures", "ph_tax_eval_dataset.csv",
)


def _d(val):
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _load_rates():
    with open(_BIR_RATES) as f:
        return json.load(f)


def _load_eval_rows():
    rows = []
    with open(_BIR_EVAL_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row.get("scenario_id", "").strip()
            if not sid or sid.startswith("#"):
                continue
            rows.append(row)
    return rows


def _build_invoice_from_vat_scenario(row):
    """Build an invoice doc from a VAT output scenario.

    VAT output scenarios provide:
      - gross_amount (VAT-inclusive for standard)
      - expected_tax_rate (0.12 or 0.00)
      - expected_tax_amount (VAT amount)
      - expected_net (net of VAT)

    We construct a full invoice document suitable for ph_invoice_math.validate().
    """
    gross_amount = float(row["gross_amount"])
    vat_rate = float(row["expected_tax_rate"])
    vat_amount = float(row["expected_tax_amount"])
    net_of_vat = float(row["expected_net"])

    # Use 2% EWT on the net amount (standard professional services)
    withholding_rate = 0.02
    withholding_amount = float(_d(Decimal(str(net_of_vat)) * Decimal("0.02")))

    gross_total = float(_d(Decimal(str(net_of_vat)) + Decimal(str(vat_amount))))
    printed_total_due = float(_d(
        Decimal(str(gross_total)) - Decimal(str(withholding_amount))
    ))

    return {
        "lines": [
            {
                "description": f"Service — {row['scenario_id']}",
                "qty": 1,
                "unit_cost": net_of_vat,
                "amount": net_of_vat,
            },
        ],
        "net_of_vat": net_of_vat,
        "vat_rate": vat_rate,
        "vat_amount": vat_amount,
        "gross_total": gross_total,
        "withholding_rate": withholding_rate,
        "withholding_amount": withholding_amount,
        "printed_total_due": printed_total_due,
    }


def _build_invoice_with_wrong_total(row):
    """Same as above but printed_total_due excludes VAT (common mistake)."""
    doc = _build_invoice_from_vat_scenario(row)
    # Simulate common error: printed total = net - withholding (missing VAT)
    net = Decimal(str(doc["net_of_vat"]))
    wh = Decimal(str(doc["withholding_amount"]))
    doc["printed_total_due"] = float(_d(net - wh))
    return doc


class TestEvalBridgeVatOutput(unittest.TestCase):
    """BIR eval VAT output scenarios → ph_invoice_math validator."""

    @classmethod
    def setUpClass(cls):
        cls.rows = [
            r for r in _load_eval_rows()
            if r["category"] == "vat"
            and r["subcategory"].startswith("output_standard")
            and float(r["expected_tax_rate"]) > 0
            and float(r["gross_amount"]) > 0
        ]
        assert len(cls.rows) >= 2, (
            f"Need >=2 standard VAT output scenarios, got {len(cls.rows)}"
        )

    def test_correct_invoices_pass(self):
        """Invoices built with correct math from eval data should validate."""
        for row in self.rows:
            doc = _build_invoice_from_vat_scenario(row)
            result = validate(doc)
            self.assertEqual(
                result["status"], "validated",
                f"{row['scenario_id']}: expected validated, got "
                f"{result['status']} — findings: {result['findings']}"
            )

    def test_wrong_printed_total_flagged(self):
        """Invoices with net-only printed total (missing VAT) are flagged."""
        for row in self.rows:
            doc = _build_invoice_with_wrong_total(row)
            result = validate(doc)
            codes = [f["code"] for f in result["findings"]]
            self.assertIn(
                "PRINTED_TOTAL_DUE_MISMATCH", codes,
                f"{row['scenario_id']}: expected PRINTED_TOTAL_DUE_MISMATCH"
            )

    def test_wrong_vat_amount_flagged(self):
        """Invoice with tampered VAT amount is caught."""
        for row in self.rows:
            doc = _build_invoice_from_vat_scenario(row)
            # Tamper: halve the VAT
            doc["vat_amount"] = float(_d(
                Decimal(str(doc["vat_amount"])) / Decimal("2")
            ))
            result = validate(doc)
            codes = [f["code"] for f in result["findings"]]
            self.assertIn(
                "VAT_MISMATCH", codes,
                f"{row['scenario_id']}: expected VAT_MISMATCH"
            )


class TestEvalBridgeZeroRated(unittest.TestCase):
    """Zero-rated and exempt VAT scenarios should validate with 0% VAT."""

    @classmethod
    def setUpClass(cls):
        cls.rows = [
            r for r in _load_eval_rows()
            if r["category"] == "vat"
            and ("zero" in r["subcategory"] or "exempt" in r["subcategory"])
            and float(r["gross_amount"]) > 0
        ]

    def test_zero_rated_invoices_pass(self):
        """Zero-rated/exempt invoices with correct math pass validation."""
        for row in self.rows:
            doc = _build_invoice_from_vat_scenario(row)
            result = validate(doc)
            self.assertEqual(
                result["status"], "validated",
                f"{row['scenario_id']}: expected validated, got "
                f"{result['status']} — findings: {result['findings']}"
            )


class TestEvalBridgeEwt(unittest.TestCase):
    """BIR eval EWT scenarios → validator withholding check."""

    @classmethod
    def setUpClass(cls):
        cls.rates = _load_rates()
        cls.ewt_rates = cls.rates["expanded_withholding_tax"]
        cls.rows = [
            r for r in _load_eval_rows()
            if r["category"] == "ewt"
            and r.get("atc_code", "").strip()
            and "+" not in r.get("atc_code", "")
            and r.get("subcategory") != "combined_vat_ewt"
            and float(r.get("gross_amount", 0)) > 0
        ]
        assert len(cls.rows) >= 5, (
            f"Need >=5 EWT scenarios, got {len(cls.rows)}"
        )

    def test_ewt_withholding_correct(self):
        """Invoices with correct EWT withholding pass validation."""
        for row in self.rows:
            atc = row["atc_code"].strip()
            rate_entry = self.ewt_rates.get(atc)
            if not rate_entry:
                continue
            ewt_rate = rate_entry["rate"]
            gross = float(row["gross_amount"])
            net = gross  # EWT scenarios: gross_amount IS the base
            vat_rate = 0.12
            vat_amount = float(_d(Decimal(str(net)) * Decimal(str(vat_rate))))
            gross_total = float(_d(Decimal(str(net)) + Decimal(str(vat_amount))))
            wh_amount = float(_d(Decimal(str(net)) * Decimal(str(ewt_rate))))
            printed_total = float(_d(
                Decimal(str(gross_total)) - Decimal(str(wh_amount))
            ))

            doc = {
                "lines": [{
                    "description": f"EWT {atc} — {row['scenario_id']}",
                    "qty": 1,
                    "unit_cost": net,
                    "amount": net,
                }],
                "net_of_vat": net,
                "vat_rate": vat_rate,
                "vat_amount": vat_amount,
                "gross_total": gross_total,
                "withholding_rate": ewt_rate,
                "withholding_amount": wh_amount,
                "printed_total_due": printed_total,
            }
            result = validate(doc)
            self.assertEqual(
                result["status"], "validated",
                f"{row['scenario_id']} (ATC {atc}): expected validated, "
                f"findings: {result['findings']}"
            )

    def test_wrong_withholding_flagged(self):
        """Invoices with wrong withholding amount are flagged."""
        row = self.rows[0]
        atc = row["atc_code"].strip()
        rate_entry = self.ewt_rates.get(atc)
        if not rate_entry:
            self.skipTest(f"ATC {atc} not in rate file")
        ewt_rate = rate_entry["rate"]
        gross = float(row["gross_amount"])
        net = gross
        vat_amount = float(_d(Decimal(str(net)) * Decimal("0.12")))
        gross_total = float(_d(Decimal(str(net)) + Decimal(str(vat_amount))))

        doc = {
            "lines": [{"description": "test", "qty": 1,
                        "unit_cost": net, "amount": net}],
            "net_of_vat": net,
            "vat_rate": 0.12,
            "vat_amount": vat_amount,
            "gross_total": gross_total,
            "withholding_rate": ewt_rate,
            "withholding_amount": 999.99,  # wrong
            "printed_total_due": float(_d(
                Decimal(str(gross_total)) - Decimal("999.99")
            )),
        }
        result = validate(doc)
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("WITHHOLDING_MISMATCH", codes)


class TestEvalBridgeDataverseFlagship(unittest.TestCase):
    """The flagship Dataverse/TBWA invoice that caught the LLM hallucination.

    This test ensures the bridge between BIR rate data and the invoice
    validator catches the exact pattern that fooled the LLM: printed
    total = net - withholding (₱85,000) instead of gross - withholding
    (₱95,408.16).
    """

    def test_dataverse_pattern_from_rates(self):
        """Construct Dataverse-like invoice using BIR rates, verify mismatch."""
        rates = _load_rates()
        vat_rate = rates["vat"]["standard_rate"]  # 0.12
        ewt_rate = rates["expanded_withholding_tax"]["WC020"]["rate"]  # 0.02

        net_of_vat = Decimal("86734.69")
        vat_amount = _d(net_of_vat * Decimal(str(vat_rate)))
        gross_total = _d(net_of_vat + vat_amount)
        withholding = _d(net_of_vat * Decimal(str(ewt_rate)))

        # Common error: printed total uses net - withholding
        wrong_printed = _d(net_of_vat - withholding)
        correct_printed = _d(gross_total - withholding)

        doc_wrong = {
            "lines": [{"description": "Prof Svcs", "qty": 1,
                        "unit_cost": float(net_of_vat),
                        "amount": float(net_of_vat)}],
            "net_of_vat": float(net_of_vat),
            "vat_rate": vat_rate,
            "vat_amount": float(vat_amount),
            "gross_total": float(gross_total),
            "withholding_rate": ewt_rate,
            "withholding_amount": float(withholding),
            "printed_total_due": float(wrong_printed),
        }

        result = validate(doc_wrong)
        self.assertEqual(result["status"], "needs_review")
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("PRINTED_TOTAL_DUE_MISMATCH", codes)

        mismatch = next(
            f for f in result["findings"]
            if f["code"] == "PRINTED_TOTAL_DUE_MISMATCH"
        )
        # Delta should equal VAT amount (the common ₱10,408.16 pattern)
        self.assertEqual(mismatch["delta"], str(vat_amount))

        # Now verify the correct version passes
        doc_correct = deepcopy(doc_wrong)
        doc_correct["printed_total_due"] = float(correct_printed)
        result_ok = validate(doc_correct)
        self.assertEqual(result_ok["status"], "validated")


if __name__ == "__main__":
    unittest.main()
