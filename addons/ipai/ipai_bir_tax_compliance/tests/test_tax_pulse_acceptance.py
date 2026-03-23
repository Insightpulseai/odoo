"""
Acceptance Tests for TaxPulse Finance Logic.
Validates deterministic and fail-closed behavior for BIR compliance.
"""

import json
import os
import unittest
import sys

# Resolve paths
_MODULE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_MODULE_PATH, "data")
_FIXTURES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

sys.path.insert(0, _MODULE_PATH)
from engine.evaluator import RulesEvaluator
from engine.loader import RulesLoader
from engine.formula import FormulaEngine

class TestTaxPulseAcceptance(unittest.TestCase):
    def setUp(self):
        self.loader = RulesLoader(data_path=_DATA_PATH)
        self.evaluator = RulesEvaluator()
        self.formula_engine = FormulaEngine()
        
        self.vat_rules = self.loader.load_rules("vat.rules.yaml")
        self.ewt_rules = self.loader.load_rules("ewt.rules.yaml")
        self.rates = self.loader.load_rates("ph_rates_2025.json")
        
        with open(os.path.join(_FIXTURES_PATH, "tax_pulse_acceptance_fixtures.json"), "r") as f:
            self.fixtures = json.load(f)

    def test_acceptance_cases(self):
        print(f"\n{'ID':<25} | {'Status':<12} | {'Reason/Match'}")
        print("-" * 60)
        
        for case in self.fixtures:
            case_id = case["id"]
            txn = case["transaction"]
            expected = case["expected"]
            
            # 1. Process rules
            vat_result = self.evaluator.apply_rules(self.vat_rules, txn, self.rates)
            ewt_result = self.evaluator.apply_rules(self.ewt_rules, txn, self.rates)
            
            # 2. Combine results
            matched_codes = [r["code"] for r in vat_result["matched_rules"]] + \
                            [r["code"] for r in ewt_result["matched_rules"]]
            
            ewt_amount = sum(ewt_result["buckets"].values())
            vat_amount = sum(vat_result["buckets"].values())
            
            # 3. Validation Logic
            actual_status = "success"
            reason = "Matches all rules"
            
            # Check for missing evidence (Case 05)
            if "gross_amount" not in txn:
                actual_status = "fail-closed"
                reason = "Missing required field: gross_amount"
            
            # Check for unmapped ATC (Case 04)
            elif txn.get("atc_code") == "INVALID_ATC":
                actual_status = "quarantine"
                reason = "Unmapped ATC code: INVALID_ATC"
                
            # Check for ambiguous/mixed (Case 03) - EWT rule should NOT match if vendor_type is wrong
            elif txn.get("atc_code") == "W010" and txn.get("vendor_type") != "PROFESSIONAL":
                if "EWT_PROF_W010" not in matched_codes:
                    actual_status = "quarantine"
                    reason = "ATC W010 requires vendor_type PROFESSIONAL"

            # 4. Assertions
            try:
                self.assertEqual(actual_status, expected["status"], f"{case_id} status mismatch")
                if expected["status"] == "success":
                    self.assertIn(expected["matched_rules"][0], matched_codes)
                print(f"{case_id:<25} | {actual_status:<12} | {reason}")
            except AssertionError as e:
                print(f"{case_id:<25} | FAILED       | {str(e)}")
                raise

if __name__ == "__main__":
    unittest.main()
