"""Tests expected row counts in bronze seed CSVs."""
import csv
from pathlib import Path

import pytest

SEED = Path(__file__).parent.parent.parent / "lakeflow_ingestion" / "seed" / "bronze"


def _count(filename):
    with open(SEED / filename, newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


class TestRowCounts:
    """Validate that seed fixtures have the expected cardinality."""

    def test_projects_count(self):
        assert _count("projects.csv") == 3

    def test_tasks_minimum(self):
        n = _count("tasks.csv")
        assert n >= 10, f"Expected >= 10 tasks, got {n}"

    def test_employees_count(self):
        assert _count("employees.csv") == 5

    def test_gl_journal_entries_minimum(self):
        n = _count("gl_journal_entries.csv")
        assert n >= 20, f"Expected >= 20 GL entries, got {n}"

    def test_vendor_bills_count(self):
        assert _count("vendor_bills.csv") == 4

    def test_invoices_count(self):
        assert _count("invoices.csv") == 4

    def test_cash_advances_count(self):
        assert _count("cash_advances.csv") == 2

    def test_budgets_count(self):
        assert _count("budgets.csv") == 9


class TestVendorBillStatuses:
    """Vendor bills must cover all 4 lifecycle statuses."""

    def test_all_statuses_present(self):
        with open(SEED / "vendor_bills.csv", newline="") as f:
            statuses = {row["status"] for row in csv.DictReader(f)}
        expected = {"draft", "open", "paid", "overdue"}
        assert expected == statuses, (
            f"Expected statuses {expected}, got {statuses}"
        )
