from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from ipai_data_intelligence.seeding.load_finance_seed_to_databricks import DatabricksSqlClient


@dataclass
class AssertionOutcome:
    name: str
    passed: bool
    details: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run end-to-end Databricks assertions for finance seed marts.")
    parser.add_argument("--host", default=os.getenv("DATABRICKS_HOST"))
    parser.add_argument("--token", default=os.getenv("DATABRICKS_TOKEN"))
    parser.add_argument("--warehouse-id", default=os.getenv("DATABRICKS_WAREHOUSE_ID"))
    parser.add_argument("--catalog", default=os.getenv("DATABRICKS_CATALOG", "dbw_ipai_dev"))
    parser.add_argument("--gold-schema", default=os.getenv("DATABRICKS_GOLD_SCHEMA", "gold"))
    parser.add_argument(
        "--evidence-path",
        default="artifacts/databricks-finance-seed/assertion_evidence.json",
        help="Where to write assertion evidence JSON.",
    )
    return parser.parse_args()


def require(value: str | None, name: str) -> str:
    if not value:
        raise ValueError(f"Missing required setting: {name}")
    return value


def to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def write_evidence(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def describe_columns(client: DatabricksSqlClient, fq_table: str) -> set[str]:
    rows = client.query_rows(f"DESCRIBE TABLE {fq_table}")
    available = set()
    for row in rows:
        column_name = row.get("col_name") or row.get("col_name ")
        if not column_name:
            continue
        name = str(column_name).strip()
        if not name or name.startswith("#"):
            continue
        available.add(name)
    return available


def choose_column(available: set[str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in available:
            return candidate
    return None


def assert_row_count(
    client: DatabricksSqlClient,
    fq_table: str,
    *,
    exact: int | None = None,
    minimum: int | None = None,
) -> AssertionOutcome:
    count = int(client.query_scalar(f"SELECT COUNT(*) AS row_count FROM {fq_table}"))
    if exact is not None and count != exact:
        return AssertionOutcome(f"row_count:{fq_table}", False, f"expected {exact}, got {count}")
    if minimum is not None and count < minimum:
        return AssertionOutcome(f"row_count:{fq_table}", False, f"expected at least {minimum}, got {count}")
    return AssertionOutcome(f"row_count:{fq_table}", True, f"count={count}")


def assert_project_scenarios(client: DatabricksSqlClient, fq_table: str) -> AssertionOutcome:
    columns = describe_columns(client, fq_table)
    project_name_col = choose_column(columns, ["project_name", "name", "project"])
    budget_col = choose_column(columns, ["budget_amount", "budget", "planned_budget"])
    actual_col = choose_column(columns, ["actual_cost", "actual_amount", "actual_spend", "actuals"])
    margin_col = choose_column(columns, ["margin_pct", "margin_percent", "margin", "gross_margin_pct"])

    if not project_name_col:
        return AssertionOutcome(
            "project_scenarios",
            False,
            f"missing project-name column on {fq_table}; available={sorted(columns)}",
        )

    rows = client.query_rows(f"SELECT * FROM {fq_table}")
    if not rows:
        return AssertionOutcome("project_scenarios", False, "table has no rows")

    def find_project_row(keyword: str) -> dict[str, Any] | None:
        for row in rows:
            value = str(row.get(project_name_col, "")).lower()
            if keyword in value:
                return row
        return None

    alpha = find_project_row("alpha")
    beta = find_project_row("beta")
    gamma = find_project_row("gamma")

    if not alpha or not beta or not gamma:
        return AssertionOutcome("project_scenarios", False, "missing one or more scenario rows for Alpha/Beta/Gamma")

    details: list[str] = ["found Alpha/Beta/Gamma"]

    if budget_col and actual_col:
        alpha_budget = to_decimal(alpha.get(budget_col))
        alpha_actual = to_decimal(alpha.get(actual_col))
        beta_budget = to_decimal(beta.get(budget_col))
        beta_actual = to_decimal(beta.get(actual_col))
        gamma_budget = to_decimal(gamma.get(budget_col))
        gamma_actual = to_decimal(gamma.get(actual_col))

        if None not in {alpha_budget, alpha_actual, beta_budget, beta_actual, gamma_budget, gamma_actual}:
            if not alpha_actual < alpha_budget:
                return AssertionOutcome("project_scenarios", False, "Alpha should be under budget")
            if not beta_actual > beta_budget:
                return AssertionOutcome("project_scenarios", False, "Beta should be over budget")
            if not gamma_actual < gamma_budget:
                return AssertionOutcome("project_scenarios", False, "Gamma should be underspent vs budget")
            details.append("budget/actual scenario checks passed")

    if margin_col:
        alpha_margin = to_decimal(alpha.get(margin_col))
        beta_margin = to_decimal(beta.get(margin_col))
        if alpha_margin is not None and beta_margin is not None:
            if not alpha_margin > 0:
                return AssertionOutcome("project_scenarios", False, "Alpha should have positive margin")
            if not beta_margin < 0:
                return AssertionOutcome("project_scenarios", False, "Beta should have negative margin")
            details.append("margin checks passed")

    return AssertionOutcome("project_scenarios", True, "; ".join(details))


def assert_expense_liquidation(client: DatabricksSqlClient, fq_table: str) -> AssertionOutcome:
    columns = describe_columns(client, fq_table)
    outstanding_col = choose_column(
        columns,
        ["unliquidated_advance_amount", "outstanding_advance_amount", "open_advance_amount", "outstanding_amount"],
    )

    rows = client.query_rows(f"SELECT * FROM {fq_table}")
    if len(rows) != 5:
        return AssertionOutcome("expense_liquidation", False, f"expected 5 employee rows, got {len(rows)}")

    if outstanding_col:
        found_open_advance = False
        for row in rows:
            amount = to_decimal(row.get(outstanding_col))
            if amount is not None and amount > 0:
                found_open_advance = True
                break
        if not found_open_advance:
            return AssertionOutcome("expense_liquidation", False, "expected at least one unliquidated advance")
        return AssertionOutcome("expense_liquidation", True, "5 rows; open advance scenario detected")

    return AssertionOutcome("expense_liquidation", True, "5 rows; outstanding-advance column not present, count-only assertion used")


def main() -> int:
    args = parse_args()

    client = DatabricksSqlClient(
        host=require(args.host, "DATABRICKS_HOST / --host"),
        token=require(args.token, "DATABRICKS_TOKEN / --token"),
        warehouse_id=require(args.warehouse_id, "DATABRICKS_WAREHOUSE_ID / --warehouse-id"),
    )

    gold = lambda table: f"{args.catalog}.{args.gold_schema}.{table}"

    outcomes = [
        assert_row_count(client, gold("project_profitability"), exact=3),
        assert_row_count(client, gold("project_budget_vs_actual"), exact=9),
        assert_row_count(client, gold("expense_liquidation_health"), exact=5),
        assert_row_count(client, gold("ap_ar_cash_summary"), minimum=1),
        assert_row_count(client, gold("policy_compliance_scorecard"), minimum=1),
        assert_row_count(client, gold("portfolio_financial_health"), exact=1),
        assert_project_scenarios(client, gold("project_profitability")),
        assert_expense_liquidation(client, gold("expense_liquidation_health")),
    ]

    payload = {
        "catalog": args.catalog,
        "gold_schema": args.gold_schema,
        "outcomes": [outcome.__dict__ for outcome in outcomes],
        "passed": all(outcome.passed for outcome in outcomes),
    }
    write_evidence(Path(args.evidence_path), payload)

    for outcome in outcomes:
        print(f"[{'PASS' if outcome.passed else 'FAIL'}] {outcome.name}: {outcome.details}")

    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
