"""Eval dataset test runner — validates ph_tax_eval_dataset.csv against ph_rates_2025.json.

Loads ~130 scenarios across 22 categories and verifies:
- EWT rate lookups match expected rates
- FWT rate lookups match expected rates (resident + non-resident)
- VAT computation (12% standard, 0% zero-rated/exempt)
- PIT graduated bracket computation
- CIT rate verification
- CGT rate verification
- Percentage tax rate verification
- Capital gains tax rate verification

Scenarios that test behavioral logic (approval, SoD, TIN validation, filing deadlines,
SLSP reconciliation, 2307 generation) are validated structurally but not computationally,
since they require Odoo runtime.

Runs standalone without Odoo.
"""

import csv
import json
import os
import unittest
from decimal import Decimal, ROUND_HALF_UP

_MODULE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_MODULE_PATH, "data")
_FIXTURES_PATH = os.path.join(_MODULE_PATH, "tests", "fixtures")


def _load_rates():
    with open(os.path.join(_DATA_PATH, "rates", "ph_rates_2025.json")) as f:
        return json.load(f)


def _load_eval_dataset():
    """Load eval CSV, skip comment/blank lines."""
    rows = []
    with open(os.path.join(_FIXTURES_PATH, "ph_tax_eval_dataset.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row.get("scenario_id", "").strip()
            if not sid or sid.startswith("#"):
                continue
            rows.append(row)
    return rows


def _compute_pit(annual_income):
    """Compute PH individual income tax using TRAIN graduated brackets."""
    brackets = [
        (250000, 0.00, 0, 0),
        (400000, 0.15, 250000, 0),
        (800000, 0.20, 400000, 22500),
        (2000000, 0.25, 800000, 102500),
        (8000000, 0.30, 2000000, 402500),
        (None, 0.35, 8000000, 2202500),
    ]
    for ceiling, rate, excess_over, fixed in brackets:
        if ceiling is None or annual_income <= ceiling:
            if rate == 0.0:
                return 0.0
            return fixed + rate * (annual_income - excess_over)
    return 0.0


def _get_rate_from_json(rates, atc_code, category, subcategory):
    """Look up the expected rate from ph_rates_2025.json for a given scenario."""
    if not atc_code:
        return None

    # EWT codes
    ewt = rates.get("expanded_withholding_tax", {})
    if atc_code in ewt:
        return ewt[atc_code]["rate"]

    # FWT codes
    fwt = rates.get("final_withholding_tax", {})
    for sub in ("resident", "non_resident"):
        section = fwt.get(sub, {})
        if atc_code in section:
            return section[atc_code]["rate"]

    return None


class TestEvalDatasetStructure(unittest.TestCase):
    """Structural validation of the eval dataset itself."""

    @classmethod
    def setUpClass(cls):
        cls.rows = _load_eval_dataset()
        cls.rates = _load_rates()

    def test_dataset_loads(self):
        """Eval dataset loads with >100 scenarios."""
        self.assertGreater(len(self.rows), 100, "Expected >100 scenarios")

    def test_all_scenario_ids_unique(self):
        """Every scenario_id is unique."""
        ids = [r["scenario_id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)), f"Duplicate IDs: {[x for x in ids if ids.count(x) > 1]}")

    def test_all_categories_present(self):
        """Dataset covers all major tax categories."""
        categories = {r["category"] for r in self.rows}
        expected = {"vat", "ewt", "fwt", "cit", "pit", "cgt", "percentage_tax"}
        missing = expected - categories
        self.assertFalse(missing, f"Missing categories: {missing}")

    def test_required_columns_present(self):
        """All required columns exist in the CSV."""
        required = {
            "scenario_id", "category", "subcategory", "gross_amount",
            "currency", "expected_tax_rate", "expected_tax_amount",
            "expected_behavior", "authority",
        }
        actual = set(self.rows[0].keys())
        missing = required - actual
        self.assertFalse(missing, f"Missing columns: {missing}")

    def test_all_ewt_atc_codes_in_rate_file(self):
        """Every ATC code used in EWT scenarios exists in ph_rates_2025.json."""
        ewt_codes = rates_ewt_codes = set(self.rates["expanded_withholding_tax"].keys())
        for row in self.rows:
            if row["category"] != "ewt":
                continue
            atc = row.get("atc_code", "").strip()
            if not atc or "+" in atc:  # skip multi-ATC
                continue
            self.assertIn(
                atc, ewt_codes,
                f"{row['scenario_id']}: ATC {atc} not in rate file"
            )

    def test_all_fwt_codes_in_rate_file(self):
        """Every FWT code used in FWT scenarios exists in ph_rates_2025.json."""
        fwt = self.rates["final_withholding_tax"]
        all_fwt_codes = set()
        for sub in ("resident", "non_resident"):
            all_fwt_codes.update(fwt.get(sub, {}).keys())

        for row in self.rows:
            if row["category"] != "fwt":
                continue
            atc = row.get("atc_code", "").strip()
            if not atc:
                continue
            # Treaty scenarios use statutory code but apply treaty rate
            if row["subcategory"].startswith("treaty_"):
                continue
            self.assertIn(
                atc, all_fwt_codes,
                f"{row['scenario_id']}: FWT code {atc} not in rate file"
            )


class TestEvalEwtRates(unittest.TestCase):
    """Validate EWT scenarios against ph_rates_2025.json rates."""

    @classmethod
    def setUpClass(cls):
        cls.rows = [r for r in _load_eval_dataset() if r["category"] == "ewt"]
        cls.rates = _load_rates()
        cls.ewt = cls.rates["expanded_withholding_tax"]

    def test_ewt_rate_lookups(self):
        """Each EWT scenario's expected_tax_rate matches the rate file."""
        for row in self.rows:
            atc = row.get("atc_code", "").strip()
            if not atc or "+" in atc:
                continue
            expected_rate = row["expected_tax_rate"]
            if expected_rate in ("n/a", "mixed", ""):
                continue
            # Skip combined VAT+EWT scenarios (rate is sum of both taxes)
            if row["subcategory"] == "combined_vat_ewt":
                continue
            expected_rate = float(expected_rate)
            actual_rate = self.ewt.get(atc, {}).get("rate")
            self.assertIsNotNone(
                actual_rate,
                f"{row['scenario_id']}: ATC {atc} missing from rate file"
            )
            self.assertAlmostEqual(
                actual_rate, expected_rate, places=4,
                msg=f"{row['scenario_id']}: rate mismatch for {atc} — "
                    f"file={actual_rate}, expected={expected_rate}"
            )

    def test_ewt_amount_computation(self):
        """EWT amount = gross * rate for standard EWT scenarios."""
        for row in self.rows:
            atc = row.get("atc_code", "").strip()
            if not atc or "+" in atc:
                continue
            expected_amt = row["expected_tax_amount"]
            if expected_amt in ("n/a", ""):
                continue
            expected_amt = float(expected_amt)
            gross = float(row["gross_amount"])
            rate = self.ewt.get(atc, {}).get("rate")
            if rate is None:
                continue
            # For combined VAT+EWT (EWT-EDGE-004), the base is gross/1.12
            if row["subcategory"] == "combined_vat_ewt":
                continue
            computed = round(gross * rate, 2)
            self.assertAlmostEqual(
                computed, expected_amt, places=2,
                msg=f"{row['scenario_id']}: amount mismatch — "
                    f"computed={computed}, expected={expected_amt}"
            )


class TestEvalFwtRates(unittest.TestCase):
    """Validate FWT scenarios against ph_rates_2025.json rates."""

    @classmethod
    def setUpClass(cls):
        cls.rows = [r for r in _load_eval_dataset() if r["category"] == "fwt"]
        cls.rates = _load_rates()
        cls.fwt = cls.rates["final_withholding_tax"]

    def _lookup_fwt_rate(self, code):
        for sub in ("resident", "non_resident"):
            section = self.fwt.get(sub, {})
            if code in section:
                return section[code]["rate"]
        return None

    def test_fwt_statutory_rate_lookups(self):
        """Each non-treaty FWT scenario's rate matches the rate file."""
        for row in self.rows:
            if row["subcategory"].startswith("treaty_"):
                continue
            atc = row.get("atc_code", "").strip()
            if not atc:
                continue
            expected_rate = float(row["expected_tax_rate"])
            actual_rate = self._lookup_fwt_rate(atc)
            self.assertIsNotNone(
                actual_rate,
                f"{row['scenario_id']}: FWT code {atc} missing"
            )
            self.assertAlmostEqual(
                actual_rate, expected_rate, places=4,
                msg=f"{row['scenario_id']}: rate mismatch for {atc}"
            )

    def test_fwt_amount_computation(self):
        """FWT amount = gross * rate for non-treaty scenarios."""
        for row in self.rows:
            if row["subcategory"].startswith("treaty_"):
                continue
            atc = row.get("atc_code", "").strip()
            if not atc:
                continue
            gross = float(row["gross_amount"])
            rate = self._lookup_fwt_rate(atc)
            if rate is None:
                continue
            expected_amt = float(row["expected_tax_amount"])
            computed = round(gross * rate, 2)
            self.assertAlmostEqual(
                computed, expected_amt, places=2,
                msg=f"{row['scenario_id']}: amount mismatch — "
                    f"computed={computed}, expected={expected_amt}"
            )

    def test_treaty_rates_lower_than_statutory(self):
        """Treaty FWT rates must be strictly lower than statutory rates."""
        for row in self.rows:
            if not row["subcategory"].startswith("treaty_"):
                continue
            atc = row.get("atc_code", "").strip()
            treaty_rate = float(row["expected_tax_rate"])
            statutory_rate = self._lookup_fwt_rate(atc)
            if statutory_rate is None:
                continue
            self.assertLess(
                treaty_rate, statutory_rate,
                f"{row['scenario_id']}: treaty rate {treaty_rate} not less than "
                f"statutory {statutory_rate} for {atc}"
            )


class TestEvalVatRates(unittest.TestCase):
    """Validate VAT scenarios against ph_rates_2025.json."""

    @classmethod
    def setUpClass(cls):
        cls.rows = [r for r in _load_eval_dataset() if r["category"] == "vat"]
        cls.rates = _load_rates()

    def test_vat_standard_rate(self):
        """Standard VAT scenarios use 12%."""
        for row in self.rows:
            if row["expected_tax_rate"] in ("n/a", "0.00", ""):
                continue
            # Skip percentage_tax crossover scenario (VAT-OUT-009)
            if row.get("tax_type") == "percentage_tax":
                continue
            rate = float(row["expected_tax_rate"])
            if rate > 0:
                self.assertAlmostEqual(
                    rate, self.rates["vat"]["standard_rate"], places=4,
                    msg=f"{row['scenario_id']}: VAT rate mismatch"
                )

    def test_zero_rated_is_zero(self):
        """Zero-rated and exempt scenarios have 0% tax."""
        for row in self.rows:
            if "zero" in row["subcategory"] or "exempt" in row["subcategory"]:
                rate = float(row["expected_tax_rate"])
                self.assertEqual(
                    rate, 0.0,
                    f"{row['scenario_id']}: zero/exempt should be 0%"
                )


class TestEvalPitBrackets(unittest.TestCase):
    """Validate PIT graduated bracket computation."""

    @classmethod
    def setUpClass(cls):
        cls.rows = [r for r in _load_eval_dataset() if r["category"] == "pit"]
        cls.rates = _load_rates()

    def test_pit_bracket_computation(self):
        """PIT tax for each bracket matches TRAIN Law graduated rates."""
        for row in self.rows:
            income = float(row["gross_amount"])
            expected_tax = float(row["expected_tax_amount"])
            computed = _compute_pit(income)
            self.assertAlmostEqual(
                computed, expected_tax, places=2,
                msg=f"{row['scenario_id']}: PIT mismatch — "
                    f"income={income}, computed={computed}, expected={expected_tax}"
            )

    def test_pit_brackets_match_rate_file(self):
        """Rate file compensation_tax ranges match TRAIN brackets."""
        brackets = self.rates["compensation_tax"]["ranges"]
        self.assertEqual(len(brackets), 6, "Expected 6 PIT brackets")
        self.assertEqual(brackets[0]["rate"], 0.00, "First bracket should be 0%")
        self.assertEqual(brackets[-1]["rate"], 0.35, "Last bracket should be 35%")


class TestEvalCitRates(unittest.TestCase):
    """Validate CIT scenarios."""

    @classmethod
    def setUpClass(cls):
        cls.rows = [r for r in _load_eval_dataset() if r["category"] == "cit"]
        cls.rates = _load_rates()
        cls.cit = cls.rates["corporate_income_tax"]

    def test_cit_standard(self):
        self.assertEqual(self.cit["standard_rate"], 0.25)

    def test_cit_sme(self):
        self.assertEqual(self.cit["sme_rate"], 0.20)

    def test_cit_mcit(self):
        self.assertEqual(self.cit["minimum_corporate_income_tax"], 0.01)

    def test_cit_nrfc(self):
        self.assertEqual(self.cit["nrfc_rate"], 0.25)

    def test_cit_rbe_special(self):
        self.assertEqual(self.cit["rbe_special_rate"], 0.05)

    def test_cit_scenario_rates(self):
        """Each CIT scenario's expected rate matches the rate file."""
        rate_map = {
            "standard_rate": self.cit["standard_rate"],
            "sme_rate": self.cit["sme_rate"],
            "mcit_applies": self.cit["minimum_corporate_income_tax"],
            "proprietary_edu": self.cit["proprietary_edu_nonprofit_hospital_rate"],
            "rbe_special": self.cit["rbe_special_rate"],
            "nrfc": self.cit["nrfc_rate"],
        }
        for row in self.rows:
            sub = row["subcategory"]
            expected_rate = float(row["expected_tax_rate"])
            if sub in rate_map:
                self.assertAlmostEqual(
                    rate_map[sub], expected_rate, places=4,
                    msg=f"{row['scenario_id']}: CIT rate mismatch for {sub}"
                )


class TestEvalCgtRates(unittest.TestCase):
    """Validate CGT scenarios."""

    @classmethod
    def setUpClass(cls):
        cls.rows = [r for r in _load_eval_dataset() if r["category"] == "cgt"]
        cls.rates = _load_rates()

    def test_cgt_real_property(self):
        self.assertEqual(self.rates["capital_gains_tax"]["real_property"]["rate"], 0.06)

    def test_cgt_shares(self):
        self.assertEqual(self.rates["capital_gains_tax"]["shares_not_traded"]["rate"], 0.15)

    def test_cgt_computation(self):
        """CGT amount = gross * rate for each scenario."""
        cgt = self.rates["capital_gains_tax"]
        for row in self.rows:
            sub = row["subcategory"]
            if sub == "stock_transaction_tax":
                rate = self.rates["special_taxes"]["stock_transaction_tax"]
            elif sub == "real_property":
                rate = cgt["real_property"]["rate"]
            elif sub == "shares_not_traded":
                rate = cgt["shares_not_traded"]["rate"]
            else:
                continue
            gross = float(row["gross_amount"])
            expected = float(row["expected_tax_amount"])
            computed = round(gross * rate, 2)
            self.assertAlmostEqual(
                computed, expected, places=2,
                msg=f"{row['scenario_id']}: CGT amount mismatch"
            )


class TestEvalPercentageTax(unittest.TestCase):
    """Validate percentage tax scenarios."""

    @classmethod
    def setUpClass(cls):
        cls.rows = [r for r in _load_eval_dataset() if r["category"] == "percentage_tax"]
        cls.rates = _load_rates()

    def test_standard_percentage_tax_rate(self):
        self.assertEqual(self.rates["percentage_tax"]["standard_rate"], 0.03)

    def test_percentage_tax_computation(self):
        """Percentage tax = gross * rate."""
        for row in self.rows:
            rate = float(row["expected_tax_rate"])
            gross = float(row["gross_amount"])
            expected = float(row["expected_tax_amount"])
            computed = round(gross * rate, 2)
            self.assertAlmostEqual(
                computed, expected, places=2,
                msg=f"{row['scenario_id']}: percentage tax mismatch"
            )


class TestEvalFilingDeadlines(unittest.TestCase):
    """Validate filing deadline scenarios exist in rate file."""

    @classmethod
    def setUpClass(cls):
        cls.rows = [r for r in _load_eval_dataset() if r["category"] == "deadline"]
        cls.rates = _load_rates()

    def test_all_deadline_forms_in_rate_file(self):
        """Every form referenced in deadline scenarios exists in filing_deadlines."""
        deadlines = self.rates.get("filing_deadlines", {})
        for row in self.rows:
            form = row.get("expected_form", "").strip()
            if not form:
                continue
            # Normalize: dataset uses "1601-E", rate file uses "BIR_1601E"
            key = "BIR_" + form.replace("-", "")
            self.assertIn(
                key, deadlines,
                f"{row['scenario_id']}: form {form} (key={key}) missing from filing_deadlines"
            )


class TestEvalDatasetCompleteness(unittest.TestCase):
    """Summary statistics and completeness checks."""

    @classmethod
    def setUpClass(cls):
        cls.rows = _load_eval_dataset()

    def test_scenario_count_by_category(self):
        """Report scenario counts; ensure minimum coverage per category."""
        from collections import Counter
        counts = Counter(r["category"] for r in self.rows)
        minimums = {
            "vat": 10, "ewt": 20, "fwt": 15, "cit": 5, "pit": 6,
            "cgt": 3, "percentage_tax": 2,
        }
        for cat, minimum in minimums.items():
            self.assertGreaterEqual(
                counts.get(cat, 0), minimum,
                f"Category '{cat}' has {counts.get(cat, 0)} scenarios, need >= {minimum}"
            )

    def test_covers_all_ewt_atc_families(self):
        """Dataset covers WI (professional), WC (contractor), WB (rent) families."""
        atc_codes = {
            r["atc_code"] for r in self.rows
            if r["category"] == "ewt" and r.get("atc_code")
        }
        families = {code[:2] for code in atc_codes if len(code) >= 2}
        for prefix in ("WI", "WC", "WB"):
            self.assertIn(prefix, families, f"Missing EWT family {prefix}")


if __name__ == "__main__":
    unittest.main()
