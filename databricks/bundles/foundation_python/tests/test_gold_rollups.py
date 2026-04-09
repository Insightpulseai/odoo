"""Tests expected gold-mart outputs derivable from the seeded scenarios.

These validate that the seed data encodes the intended business stories
(profitable vs. loss-making projects, budget variances, expense policy
violations, cash advance liquidation states).
"""
import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import pytest

SEED = Path(__file__).parent.parent.parent / "lakeflow_ingestion" / "seed" / "bronze"


def _rows(filename):
    with open(SEED / filename, newline="") as f:
        return list(csv.DictReader(f))


def _gl_by_project():
    """Aggregate GL revenue and cost per project."""
    agg: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: {"revenue": Decimal(0), "cost": Decimal(0)}
    )
    for r in _rows("gl_journal_entries.csv"):
        pid = r["project_id"]
        etype = r["entry_type"]
        credit = Decimal(r["credit"])
        debit = Decimal(r["debit"])
        if etype == "revenue":
            agg[pid]["revenue"] += credit
        elif etype in ("cogs", "payroll"):
            agg[pid]["cost"] += debit
    return agg


def _budget_variance(pid: str) -> Decimal:
    """Positive = over budget, negative = under budget."""
    budgets = _rows("budgets.csv")
    total_actual = sum(
        Decimal(r["actual_amount"]) for r in budgets if r["project_id"] == pid
    )
    total_planned = sum(
        Decimal(r["planned_amount"]) for r in budgets if r["project_id"] == pid
    )
    return total_actual - total_planned


class TestProjectMargins:
    """Verify the seeded project financial stories."""

    @pytest.fixture(autouse=True)
    def gl(self):
        self.agg = _gl_by_project()

    def test_alpha_positive_margin(self):
        alpha = self.agg["1"]
        margin = alpha["revenue"] - alpha["cost"]
        assert margin > 0, f"Alpha margin should be positive, got {margin}"

    def test_beta_negative_margin(self):
        beta = self.agg["2"]
        margin = beta["revenue"] - beta["cost"]
        assert margin < 0, f"Beta margin should be negative, got {margin}"

    def test_gamma_underspent(self):
        gamma = self.agg["3"]
        projects = {r["id"]: Decimal(r["budget_amount"]) for r in _rows("projects.csv")}
        assert gamma["cost"] < projects["3"], (
            f"Gamma actual cost ({gamma['cost']}) should be < budget ({projects['3']})"
        )


class TestBudgetVariance:
    """Verify budget variance directions match intended scenarios."""

    def test_alpha_under_budget(self):
        var = _budget_variance("1")
        assert var < 0, f"Alpha should be under budget (negative variance), got {var}"

    def test_beta_over_budget(self):
        var = _budget_variance("2")
        assert var > 0, f"Beta should be over budget (positive variance), got {var}"


class TestCashAdvanceLiquidation:
    """Verify cash advance liquidation percentages."""

    @pytest.fixture(autouse=True)
    def advances(self):
        self.cas = {r["id"]: r for r in _rows("cash_advances.csv")}

    def test_ca001_fully_liquidated(self):
        ca = self.cas["CA-001"]
        amount = Decimal(ca["amount"])
        liquidated = Decimal(ca["liquidated_amount"])
        pct = (liquidated / amount) * 100
        assert pct == 100, f"CA-001 should be 100% liquidated, got {pct}%"

    def test_ca002_partially_liquidated(self):
        ca = self.cas["CA-002"]
        amount = Decimal(ca["amount"])
        liquidated = Decimal(ca["liquidated_amount"])
        pct = (liquidated / amount) * 100
        assert pct < 100, f"CA-002 should be < 100% liquidated, got {pct}%"


class TestExpensePolicyFlags:
    """Verify expense compliance and receipt edge cases exist."""

    @pytest.fixture(autouse=True)
    def expenses(self):
        self.rows = _rows("expenses.csv")

    def test_at_least_one_non_compliant(self):
        non_compliant = [r for r in self.rows if r["policy_compliant"] == "false"]
        assert len(non_compliant) >= 1, "Expected at least one non-compliant expense"

    def test_at_least_one_missing_receipt(self):
        missing = [r for r in self.rows if r["has_receipt"] == "false"]
        assert len(missing) >= 1, "Expected at least one expense with has_receipt=false"
