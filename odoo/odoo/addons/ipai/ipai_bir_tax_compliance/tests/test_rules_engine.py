"""
Tests for the BIR Tax Compliance Rules Engine.

Validates the JSONLogic evaluator, formula engine, and rules loader
against golden dataset transactions and expected output.
Adapted from TaxPulse-PH-Pack/scripts/test_rules_engine.py.
"""

import csv
import json
import os
import unittest


# Resolve paths relative to this test file
_MODULE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENGINE_PATH = os.path.join(_MODULE_PATH, "engine")
_DATA_PATH = os.path.join(_MODULE_PATH, "data")
_FIXTURES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

# Import engine components directly (works both standalone and inside Odoo)
import sys
sys.path.insert(0, _MODULE_PATH)
from engine.evaluator import RulesEvaluator
from engine.formula import FormulaEngine
from engine.loader import RulesLoader


class TestRulesEvaluator(unittest.TestCase):
    """Unit tests for the JSONLogic evaluator."""

    def setUp(self):
        self.evaluator = RulesEvaluator()

    def test_equal_operator(self):
        """Equality operator matches correctly."""
        condition = {"==": [{"var": "doc_type"}, "invoice"]}
        self.assertTrue(self.evaluator.evaluate_condition(condition, {"doc_type": "invoice"}))
        self.assertFalse(self.evaluator.evaluate_condition(condition, {"doc_type": "bill"}))

    def test_not_equal_operator(self):
        """Not-equal operator works."""
        condition = {"!=": [{"var": "doc_type"}, "invoice"]}
        self.assertTrue(self.evaluator.evaluate_condition(condition, {"doc_type": "bill"}))
        self.assertFalse(self.evaluator.evaluate_condition(condition, {"doc_type": "invoice"}))

    def test_greater_than_operator(self):
        """Greater-than compares numeric values."""
        condition = {">": [{"var": "gross_amount"}, 0]}
        self.assertTrue(self.evaluator.evaluate_condition(condition, {"gross_amount": 100.0}))
        self.assertFalse(self.evaluator.evaluate_condition(condition, {"gross_amount": 0}))

    def test_less_than_operator(self):
        """Less-than compares numeric values."""
        condition = {"<": [{"var": "gross_amount"}, 1000]}
        self.assertTrue(self.evaluator.evaluate_condition(condition, {"gross_amount": 500}))
        self.assertFalse(self.evaluator.evaluate_condition(condition, {"gross_amount": 1500}))

    def test_and_operator(self):
        """AND requires all conditions to be true."""
        condition = {
            "and": [
                {"==": [{"var": "doc_type"}, "invoice"]},
                {">": [{"var": "gross_amount"}, 0]},
            ]
        }
        self.assertTrue(self.evaluator.evaluate_condition(
            condition, {"doc_type": "invoice", "gross_amount": 100}
        ))
        self.assertFalse(self.evaluator.evaluate_condition(
            condition, {"doc_type": "bill", "gross_amount": 100}
        ))

    def test_or_operator(self):
        """OR requires at least one condition to be true."""
        condition = {
            "or": [
                {"==": [{"var": "doc_type"}, "invoice"]},
                {"==": [{"var": "doc_type"}, "bill"]},
            ]
        }
        self.assertTrue(self.evaluator.evaluate_condition(
            condition, {"doc_type": "invoice"}
        ))
        self.assertTrue(self.evaluator.evaluate_condition(
            condition, {"doc_type": "bill"}
        ))
        self.assertFalse(self.evaluator.evaluate_condition(
            condition, {"doc_type": "credit_note"}
        ))

    def test_in_operator(self):
        """IN checks membership in a list."""
        condition = {"in": [{"var": "vendor_type"}, ["PROFESSIONAL", "MEDICAL"]]}
        self.assertTrue(self.evaluator.evaluate_condition(
            condition, {"vendor_type": "PROFESSIONAL"}
        ))
        self.assertFalse(self.evaluator.evaluate_condition(
            condition, {"vendor_type": "SUPPLIER"}
        ))

    def test_always_operator(self):
        """'always: true' condition always matches."""
        condition = {"always": True}
        self.assertTrue(self.evaluator.evaluate_condition(condition, {}))

    def test_empty_condition(self):
        """Empty condition defaults to True."""
        self.assertTrue(self.evaluator.evaluate_condition({}, {}))
        self.assertTrue(self.evaluator.evaluate_condition(None, {}))

    def test_arithmetic_operators(self):
        """Arithmetic operators compute correctly."""
        data = {"a": 10, "b": 3}
        self.assertEqual(
            self.evaluator._op_add(data, [{"var": "a"}, {"var": "b"}]), 13.0
        )
        self.assertEqual(
            self.evaluator._op_subtract(data, [{"var": "a"}, {"var": "b"}]), 7.0
        )
        self.assertEqual(
            self.evaluator._op_multiply(data, [{"var": "a"}, {"var": "b"}]), 30.0
        )
        self.assertAlmostEqual(
            self.evaluator._op_divide(data, [{"var": "a"}, {"var": "b"}]),
            3.3333, places=3
        )

    def test_division_by_zero(self):
        """Division by zero returns 0.0."""
        data = {"a": 10, "b": 0}
        self.assertEqual(
            self.evaluator._op_divide(data, [{"var": "a"}, {"var": "b"}]), 0.0
        )

    def test_apply_rules_vat_output(self):
        """VAT output rule matches an invoice transaction."""
        rules = [
            {
                "code": "VAT_OUTPUT_STD_12",
                "condition": {
                    "and": [
                        {"==": [{"var": "doc_type"}, "invoice"]},
                        {"==": [{"var": "tax_code"}, "VAT_12_SALES"]},
                        {">": [{"var": "gross_amount"}, 0]},
                    ]
                },
                "base_source": "gross_amount",
                "rate_value": 0.12,
                "formula": "base * rate",
                "output_bucket": "VAT_OUTPUT_12",
            }
        ]
        txn = {
            "doc_type": "invoice",
            "tax_code": "VAT_12_SALES",
            "gross_amount": 112000.00,
        }
        result = self.evaluator.apply_rules(rules, txn)
        self.assertAlmostEqual(result["buckets"]["VAT_OUTPUT_12"], 13440.0, places=2)
        self.assertEqual(len(result["matched_rules"]), 1)

    def test_apply_rules_no_match(self):
        """No rules match when conditions fail."""
        rules = [
            {
                "code": "VAT_OUTPUT_STD_12",
                "condition": {
                    "and": [
                        {"==": [{"var": "doc_type"}, "invoice"]},
                        {"==": [{"var": "tax_code"}, "VAT_12_SALES"]},
                    ]
                },
                "base_source": "gross_amount",
                "rate_value": 0.12,
                "formula": "base * rate",
                "output_bucket": "VAT_OUTPUT_12",
            }
        ]
        txn = {"doc_type": "bill", "tax_code": "VAT_12_PURCHASE", "gross_amount": 5000}
        result = self.evaluator.apply_rules(rules, txn)
        self.assertEqual(len(result["buckets"]), 0)
        self.assertEqual(len(result["matched_rules"]), 0)


class TestFormulaEngine(unittest.TestCase):
    """Unit tests for the formula engine."""

    def setUp(self):
        self.engine = FormulaEngine()

    def test_sum_function(self):
        """SUM aggregates bucket values."""
        buckets = {"VAT_OUTPUT_12": 42000.0, "VAT_OUTPUT_ZERO": 0.0}
        result = self.engine.evaluate(
            "SUM(VAT_OUTPUT_12, VAT_OUTPUT_ZERO)", buckets
        )
        self.assertAlmostEqual(result, 42000.0, places=2)

    def test_sum_minus_sum(self):
        """SUM(...) - SUM(...) computes net payable."""
        buckets = {
            "VAT_OUTPUT_12": 42000.0,
            "VAT_OUTPUT_ZERO": 0.0,
            "VAT_INPUT_12": 11160.0,
            "VAT_INPUT_ZERO": 0.0,
        }
        result = self.engine.evaluate(
            "SUM(VAT_OUTPUT_12, VAT_OUTPUT_ZERO) - SUM(VAT_INPUT_12, VAT_INPUT_ZERO)",
            buckets,
        )
        self.assertAlmostEqual(result, 30840.0, places=2)

    def test_max_function(self):
        """MAX returns the larger value."""
        buckets = {"A": 100.0, "B": 200.0}
        result = self.engine.evaluate("MAX(A, B)", buckets)
        self.assertAlmostEqual(result, 200.0, places=2)

    def test_min_function(self):
        """MIN returns the smaller value."""
        buckets = {"A": 100.0, "B": 200.0}
        result = self.engine.evaluate("MIN(A, B)", buckets)
        self.assertAlmostEqual(result, 100.0, places=2)

    def test_abs_function(self):
        """ABS returns absolute value."""
        buckets = {"A": -500.0}
        result = self.engine.evaluate("ABS(A)", buckets)
        self.assertAlmostEqual(result, 500.0, places=2)

    def test_round_function(self):
        """ROUND rounds to specified decimals."""
        buckets = {"A": 123.456789}
        result = self.engine.evaluate("ROUND(A, 2)", buckets)
        self.assertAlmostEqual(result, 123.46, places=2)

    def test_empty_formula(self):
        """Empty formula returns 0.0."""
        self.assertEqual(self.engine.evaluate("", {}), 0.0)
        self.assertEqual(self.engine.evaluate(None, {}), 0.0)

    def test_missing_bucket(self):
        """Missing bucket defaults to 0.0 in SUM."""
        buckets = {"A": 100.0}
        result = self.engine.evaluate("SUM(A, MISSING_BUCKET)", buckets)
        self.assertAlmostEqual(result, 100.0, places=2)


class TestRulesLoader(unittest.TestCase):
    """Unit tests for the rules loader."""

    def setUp(self):
        self.loader = RulesLoader(data_path=_DATA_PATH)

    def test_load_vat_rules(self):
        """VAT rules file loads and contains expected rules."""
        rules = self.loader.load_rules("vat.rules.yaml")
        self.assertGreater(len(rules), 0)
        codes = [r["code"] for r in rules]
        self.assertIn("VAT_OUTPUT_STD_12", codes)
        self.assertIn("VAT_INPUT_STD_12", codes)
        self.assertIn("VAT_PAYABLE", codes)

    def test_load_ewt_rules(self):
        """EWT rules file loads and contains expected rules."""
        rules = self.loader.load_rules("ewt.rules.yaml")
        self.assertGreater(len(rules), 0)
        codes = [r["code"] for r in rules]
        self.assertIn("EWT_PROF_W010", codes)
        self.assertIn("EWT_SUPPLIER_W157", codes)
        self.assertIn("EWT_TOTAL", codes)

    def test_load_rates(self):
        """Rates JSON loads with correct structure."""
        rates = self.loader.load_rates("ph_rates_2025.json")
        self.assertIn("vat", rates)
        self.assertIn("expanded_withholding_tax", rates)
        self.assertIn("compensation_tax", rates)
        self.assertIn("corporate_income_tax", rates)

    def test_get_rate_value_vat(self):
        """get_rate_value returns correct VAT rate."""
        rates = self.loader.load_rates("ph_rates_2025.json")
        self.assertEqual(self.loader.get_rate_value("VAT_12_SALES", rates), 0.12)
        self.assertEqual(self.loader.get_rate_value("VAT_ZERO_EXPORTS", rates), 0.00)

    def test_get_rate_value_ewt(self):
        """get_rate_value returns correct EWT rates."""
        rates = self.loader.load_rates("ph_rates_2025.json")
        self.assertEqual(self.loader.get_rate_value("W010", rates), 0.10)
        self.assertEqual(self.loader.get_rate_value("W157", rates), 0.01)
        self.assertEqual(self.loader.get_rate_value("W158", rates), 0.02)
        self.assertEqual(self.loader.get_rate_value("W169", rates), 0.05)

    def test_load_all_rules(self):
        """load_all_rules finds both VAT and EWT rule files."""
        all_rules = self.loader.load_all_rules()
        self.assertIn("vat.rules.yaml", all_rules)
        self.assertIn("ewt.rules.yaml", all_rules)

    def test_rules_sorted_by_priority(self):
        """Rules are sorted by priority descending."""
        rules = self.loader.load_rules("vat.rules.yaml")
        priorities = [r.get("priority", 0) for r in rules]
        self.assertEqual(priorities, sorted(priorities, reverse=True))

    def test_missing_rule_file(self):
        """Missing rule file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_rules("nonexistent.rules.yaml")

    def test_missing_rates_file(self):
        """Missing rates file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_rates("nonexistent_rates.json")

    def test_cache_works(self):
        """Second load returns cached data."""
        rules1 = self.loader.load_rules("vat.rules.yaml")
        rules2 = self.loader.load_rules("vat.rules.yaml")
        self.assertIs(rules1, rules2)

    def test_clear_cache(self):
        """clear_cache empties the internal caches."""
        self.loader.load_rules("vat.rules.yaml")
        self.loader.load_rates("ph_rates_2025.json")
        self.loader.clear_cache()
        self.assertEqual(len(self.loader._rules_cache), 0)
        self.assertEqual(len(self.loader._rates_cache), 0)


class TestEndToEndVatProcessing(unittest.TestCase):
    """End-to-end test: process transactions and validate VAT buckets."""

    def setUp(self):
        self.loader = RulesLoader(data_path=_DATA_PATH)
        self.evaluator = RulesEvaluator()
        self.formula_engine = FormulaEngine()

        self.vat_rules = self.loader.load_rules("vat.rules.yaml")
        self.rates = self.loader.load_rates("ph_rates_2025.json")

        # Load transactions
        self.transactions = []
        txn_file = os.path.join(_FIXTURES_PATH, "vat_basic_transactions.csv")
        with open(txn_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["gross_amount"] = float(row["gross_amount"])
                self.transactions.append(row)

    def test_vat_output_buckets(self):
        """VAT output buckets sum correctly across all transactions."""
        all_buckets = {}
        for txn in self.transactions:
            result = self.evaluator.apply_rules(self.vat_rules, txn, self.rates)
            for bucket, amount in result["buckets"].items():
                all_buckets[bucket] = all_buckets.get(bucket, 0.0) + amount

        # Output VAT: 4 invoices with VAT_12_SALES
        # TXN001=112000, TXN002=56000, TXN008=84000, TXN010=140000
        # Total output VAT = (112000+56000+84000+140000) * 0.12 = 47040
        self.assertAlmostEqual(all_buckets.get("VAT_OUTPUT_12", 0), 47040.0, places=2)

        # Zero-rated output: TXN006=224000, TXN012=168000 -> 0.0 (rate is 0%)
        self.assertAlmostEqual(all_buckets.get("VAT_OUTPUT_ZERO", 0), 0.0, places=2)

    def test_vat_input_buckets(self):
        """VAT input buckets sum correctly across purchase transactions."""
        all_buckets = {}
        for txn in self.transactions:
            result = self.evaluator.apply_rules(self.vat_rules, txn, self.rates)
            for bucket, amount in result["buckets"].items():
                all_buckets[bucket] = all_buckets.get(bucket, 0.0) + amount

        # Input VAT: bills with VAT_12_PURCHASE
        # TXN003=11200, TXN004=5600, TXN005=28000, TXN007=16800,
        # TXN009=8960, TXN011=22400, TXN013=11200
        # Total = (11200+5600+28000+16800+8960+22400+11200) * 0.12 = 12499.20
        self.assertAlmostEqual(
            all_buckets.get("VAT_INPUT_12", 0), 12499.20, places=2
        )

    def test_transaction_count(self):
        """Fixture has the expected number of transactions."""
        self.assertEqual(len(self.transactions), 13)


class TestEndToEndEwtProcessing(unittest.TestCase):
    """End-to-end test: process transactions and validate EWT buckets."""

    def setUp(self):
        self.loader = RulesLoader(data_path=_DATA_PATH)
        self.evaluator = RulesEvaluator()
        self.formula_engine = FormulaEngine()

        self.ewt_rules = self.loader.load_rules("ewt.rules.yaml")
        self.rates = self.loader.load_rates("ph_rates_2025.json")

        # Load transactions
        self.transactions = []
        txn_file = os.path.join(_FIXTURES_PATH, "vat_basic_transactions.csv")
        with open(txn_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["gross_amount"] = float(row["gross_amount"])
                self.transactions.append(row)

        # Load expected EWT
        self.expected_ewt = {}
        ewt_file = os.path.join(_FIXTURES_PATH, "ewt_expected_withholding.csv")
        with open(ewt_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["txn_id"] != "TOTAL":
                    self.expected_ewt[row["txn_id"]] = {
                        "atc_code": row["atc_code"],
                        "expected_rate": float(row["expected_ewt_rate"]),
                        "expected_amount": float(row["expected_ewt_amount"]),
                        "bucket": row["bucket_output"],
                    }

    def test_ewt_per_transaction(self):
        """Each EWT-bearing transaction computes the correct withholding amount."""
        for txn in self.transactions:
            txn_id = txn["txn_id"]
            if txn_id not in self.expected_ewt:
                continue

            expected = self.expected_ewt[txn_id]
            result = self.evaluator.apply_rules(self.ewt_rules, txn, self.rates)
            bucket_amount = result["buckets"].get(expected["bucket"], 0.0)

            self.assertAlmostEqual(
                bucket_amount,
                expected["expected_amount"],
                places=2,
                msg=f"EWT mismatch for {txn_id} (ATC {expected['atc_code']})",
            )

    def test_ewt_total(self):
        """Total EWT across all transactions matches expected 6899.20."""
        all_buckets = {}
        for txn in self.transactions:
            result = self.evaluator.apply_rules(self.ewt_rules, txn, self.rates)
            for bucket, amount in result["buckets"].items():
                all_buckets[bucket] = all_buckets.get(bucket, 0.0) + amount

        # Apply aggregation
        aggregation_rules = [
            r for r in self.ewt_rules if r.get("priority", 0) >= 200
        ]
        all_buckets = self.formula_engine.evaluate_aggregation_rules(
            aggregation_rules, all_buckets
        )

        # Manually sum individual EWT buckets for comparison
        individual_total = sum(
            v for k, v in all_buckets.items()
            if k.startswith("EWT_") and k != "EWT_TOTAL"
        )
        self.assertAlmostEqual(individual_total, 6899.20, places=2)


if __name__ == "__main__":
    unittest.main()
