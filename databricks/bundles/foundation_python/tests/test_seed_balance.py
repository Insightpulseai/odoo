"""Tests that GL journal entries balance (debits == credits)."""
import csv
from decimal import Decimal
from collections import defaultdict
from pathlib import Path

import pytest

SEED = Path(__file__).parent.parent.parent / "lakeflow_ingestion" / "seed" / "bronze"


def _load_gl():
    rows = []
    with open(SEED / "gl_journal_entries.csv", newline="") as f:
        for row in csv.DictReader(f):
            row["debit"] = Decimal(row["debit"])
            row["credit"] = Decimal(row["credit"])
            rows.append(row)
    return rows


class TestGLBalance:
    """GL journal entries must balance."""

    @pytest.fixture(autouse=True)
    def entries(self):
        self.rows = _load_gl()

    def test_total_debits_equal_credits(self):
        total_debit = sum(r["debit"] for r in self.rows)
        total_credit = sum(r["credit"] for r in self.rows)
        assert total_debit == total_credit, (
            f"Total debits ({total_debit}) != total credits ({total_credit})"
        )

    def test_entry_type_groups_balance(self):
        groups = defaultdict(lambda: {"debit": Decimal(0), "credit": Decimal(0)})
        for r in self.rows:
            groups[r["entry_type"]]["debit"] += r["debit"]
            groups[r["entry_type"]]["credit"] += r["credit"]

        for etype, totals in groups.items():
            assert totals["debit"] == totals["credit"], (
                f"entry_type '{etype}' imbalanced: "
                f"debit={totals['debit']}, credit={totals['credit']}"
            )

    def test_no_negative_amounts(self):
        for r in self.rows:
            assert r["debit"] >= 0, (
                f"Negative debit in {r['id']}: {r['debit']}"
            )
            assert r["credit"] >= 0, (
                f"Negative credit in {r['id']}: {r['credit']}"
            )
