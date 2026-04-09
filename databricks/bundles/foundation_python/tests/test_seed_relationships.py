"""Tests FK integrity across all bronze seed CSVs."""
import csv
from decimal import Decimal
from pathlib import Path

import pytest

SEED = Path(__file__).parent.parent.parent / "lakeflow_ingestion" / "seed" / "bronze"


def _ids(filename, col="id"):
    with open(SEED / filename, newline="") as f:
        return {row[col] for row in csv.DictReader(f)}


def _rows(filename):
    with open(SEED / filename, newline="") as f:
        return list(csv.DictReader(f))


def _fk_check(child_file, fk_col, parent_file, parent_col="id"):
    """Return set of orphaned FK values."""
    parent_ids = _ids(parent_file, parent_col)
    orphans = set()
    for row in _rows(child_file):
        if row[fk_col] not in parent_ids:
            orphans.add(row[fk_col])
    return orphans


class TestForeignKeys:
    """Every FK in a child CSV must reference an existing parent row."""

    def test_tasks_project_id(self):
        orphans = _fk_check("tasks.csv", "project_id", "projects.csv")
        assert not orphans, f"tasks.csv has orphan project_ids: {orphans}"

    def test_milestones_project_id(self):
        orphans = _fk_check("milestones.csv", "project_id", "projects.csv")
        assert not orphans, f"milestones.csv has orphan project_ids: {orphans}"

    def test_expenses_employee_id(self):
        orphans = _fk_check("expenses.csv", "employee_id", "employees.csv")
        assert not orphans, f"expenses.csv has orphan employee_ids: {orphans}"

    def test_vendor_bills_vendor_id(self):
        orphans = _fk_check("vendor_bills.csv", "vendor_id", "vendors.csv")
        assert not orphans, f"vendor_bills.csv has orphan vendor_ids: {orphans}"

    def test_invoices_customer_id(self):
        orphans = _fk_check("invoices.csv", "customer_id", "customers.csv")
        assert not orphans, f"invoices.csv has orphan customer_ids: {orphans}"

    def test_cash_advances_employee_id(self):
        orphans = _fk_check("cash_advances.csv", "employee_id", "employees.csv")
        assert not orphans, f"cash_advances.csv has orphan employee_ids: {orphans}"

    def test_expense_reports_employee_id(self):
        orphans = _fk_check("expense_reports.csv", "employee_id", "employees.csv")
        assert not orphans, f"expense_reports.csv has orphan employee_ids: {orphans}"

    def test_budgets_project_id(self):
        orphans = _fk_check("budgets.csv", "project_id", "projects.csv")
        assert not orphans, f"budgets.csv has orphan project_ids: {orphans}"


class TestBudgetConsistency:
    """Budget planned_amount sums must match project budget_amount."""

    def test_budget_sums_match_project(self):
        projects = {r["id"]: Decimal(r["budget_amount"]) for r in _rows("projects.csv")}
        budget_sums: dict[str, Decimal] = {}
        for row in _rows("budgets.csv"):
            pid = row["project_id"]
            budget_sums[pid] = budget_sums.get(pid, Decimal(0)) + Decimal(row["planned_amount"])

        for pid, planned_total in budget_sums.items():
            assert pid in projects, f"Budget references unknown project {pid}"
            assert planned_total == projects[pid], (
                f"Project {pid}: budget planned_amount sum ({planned_total}) "
                f"!= project budget_amount ({projects[pid]})"
            )
