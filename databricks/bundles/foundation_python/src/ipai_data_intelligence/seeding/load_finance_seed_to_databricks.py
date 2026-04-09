from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib import error, request


@dataclass
class StatementResult:
    statement_id: str
    status: str
    manifest: dict[str, Any] | None
    result: dict[str, Any] | None
    raw: dict[str, Any]


class DatabricksSqlClient:
    def __init__(self, host: str, token: str, warehouse_id: str, timeout_seconds: int = 300) -> None:
        self.host = host.rstrip("/")
        self.token = token
        self.warehouse_id = warehouse_id
        self.timeout_seconds = timeout_seconds

    def _api_request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=f"{self.host}{path}",
            method=method,
            data=body,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Databricks API error {exc.code}: {detail}") from exc

    def execute(self, statement: str, wait_seconds: int = 300) -> StatementResult:
        payload = {
            "statement": statement,
            "warehouse_id": self.warehouse_id,
            "format": "JSON_ARRAY",
            "disposition": "INLINE",
        }
        created = self._api_request("POST", "/api/2.0/sql/statements/", payload)
        statement_id = created["statement_id"]

        deadline = time.time() + wait_seconds
        while True:
            polled = self._api_request("GET", f"/api/2.0/sql/statements/{statement_id}")
            state = polled.get("status", {}).get("state", "UNKNOWN")

            if state in {"SUCCEEDED", "FAILED", "CANCELED", "CLOSED"}:
                if state != "SUCCEEDED":
                    raise RuntimeError(
                        f"Statement failed ({state}): {polled.get('status', {}).get('error', {}).get('message', 'unknown error')}\nSQL:\n{statement}"
                    )
                return StatementResult(
                    statement_id=statement_id,
                    status=state,
                    manifest=polled.get("manifest"),
                    result=polled.get("result"),
                    raw=polled,
                )

            if time.time() >= deadline:
                raise TimeoutError(f"Timed out waiting for Databricks SQL statement {statement_id}")

            time.sleep(2)

    def query_rows(self, statement: str) -> list[dict[str, Any]]:
        result = self.execute(statement)
        manifest = result.manifest or {}
        schema = manifest.get("schema", {})
        columns = [col["name"] for col in schema.get("columns", [])]
        data = (result.result or {}).get("data_array", []) or []

        rows: list[dict[str, Any]] = []
        for raw_row in data:
            rows.append({columns[idx]: raw_row[idx] for idx in range(len(columns))})
        return rows

    def query_scalar(self, statement: str) -> Any:
        rows = self.query_rows(statement)
        if not rows:
            raise RuntimeError(f"Scalar query returned no rows:\n{statement}")
        first_row = rows[0]
        return next(iter(first_row.values()))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load deterministic finance seed data into Databricks bronze/silver/gold.")
    parser.add_argument(
        "--seed-dir",
        default="databricks/bundles/lakeflow_ingestion/seed/bronze",
        help="Directory containing bronze CSV fixtures.",
    )
    parser.add_argument(
        "--gold-sql-dir",
        default="databricks/bundles/sql_warehouse/src/sql/marts",
        help="Directory containing gold mart SQL files.",
    )
    parser.add_argument(
        "--catalog",
        default=os.getenv("DATABRICKS_CATALOG", "dbw_ipai_dev"),
        help="Target Databricks catalog. Assumption: dbw_ipai_dev if not overridden.",
    )
    parser.add_argument("--bronze-schema", default=os.getenv("DATABRICKS_BRONZE_SCHEMA", "bronze"))
    parser.add_argument("--silver-schema", default=os.getenv("DATABRICKS_SILVER_SCHEMA", "silver"))
    parser.add_argument("--gold-schema", default=os.getenv("DATABRICKS_GOLD_SCHEMA", "gold"))
    parser.add_argument(
        "--evidence-path",
        default="artifacts/databricks-finance-seed/load_evidence.json",
        help="Where to write JSON evidence.",
    )
    parser.add_argument("--host", default=os.getenv("DATABRICKS_HOST"))
    parser.add_argument("--token", default=os.getenv("DATABRICKS_TOKEN"))
    parser.add_argument("--warehouse-id", default=os.getenv("DATABRICKS_WAREHOUSE_ID"))
    return parser.parse_args()


def require(value: str | None, name: str) -> str:
    if not value:
        raise ValueError(f"Missing required setting: {name}")
    return value


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header row: {path}")
        rows = [dict(row) for row in reader]
        return list(reader.fieldnames), rows


def is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_decimal(value: str) -> bool:
    try:
        Decimal(value)
        return True
    except (InvalidOperation, ValueError):
        return False


def is_iso_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def infer_sql_type(column_name: str, values: list[str]) -> str:
    non_empty = [v for v in values if v not in {"", None}]
    if not non_empty:
        return "STRING"

    lowered = column_name.lower()
    if lowered.endswith("_id") or lowered == "id":
        if all(is_int(v) for v in non_empty):
            return "BIGINT"
        return "STRING"

    if lowered.endswith("_date") or lowered == "date":
        if all(is_iso_date(v) for v in non_empty):
            return "DATE"

    if all(is_int(v) for v in non_empty):
        return "BIGINT"

    if all(is_decimal(v) for v in non_empty):
        return "DECIMAL(18,2)"

    boolean_values = {"true", "false", "1", "0", "yes", "no"}
    if all(v.strip().lower() in boolean_values for v in non_empty):
        return "BOOLEAN"

    if all(is_iso_date(v) for v in non_empty):
        return "DATE"

    return "STRING"


def sql_identifier(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError(f"Unsafe SQL identifier: {name}")
    return name


def sql_literal(value: str, sql_type: str) -> str:
    if value == "" or value is None:
        return "NULL"

    if sql_type == "BIGINT":
        return str(int(value))
    if sql_type.startswith("DECIMAL"):
        return str(Decimal(value))
    if sql_type == "BOOLEAN":
        return "TRUE" if value.strip().lower() in {"true", "1", "yes"} else "FALSE"
    if sql_type == "DATE":
        return f"DATE '{value}'"

    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def batched(items: list[Any], size: int) -> list[list[Any]]:
    return [items[idx : idx + size] for idx in range(0, len(items), size)]


def ensure_schemas(client: DatabricksSqlClient, catalog: str, bronze_schema: str, silver_schema: str, gold_schema: str) -> None:
    for schema in (bronze_schema, silver_schema, gold_schema):
        client.execute(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")


def load_bronze_table(
    client: DatabricksSqlClient,
    catalog: str,
    bronze_schema: str,
    csv_path: Path,
) -> tuple[str, int]:
    table_name = sql_identifier(csv_path.stem)
    headers, rows = read_csv_rows(csv_path)
    column_types = {
        header: infer_sql_type(header, [row.get(header, "") for row in rows])
        for header in headers
    }

    ddl_columns = ",\n  ".join(f"{sql_identifier(col)} {column_types[col]}" for col in headers)
    create_sql = f"""
    CREATE OR REPLACE TABLE {catalog}.{bronze_schema}.{table_name} (
      {ddl_columns}
    )
    USING DELTA
    """
    client.execute(create_sql)

    if not rows:
        return table_name, 0

    value_rows: list[str] = []
    for row in rows:
        rendered = ", ".join(sql_literal(row.get(col, ""), column_types[col]) for col in headers)
        value_rows.append(f"({rendered})")

    for batch in batched(value_rows, 250):
        insert_sql = f"""
        INSERT INTO {catalog}.{bronze_schema}.{table_name} ({", ".join(sql_identifier(col) for col in headers)})
        VALUES
        {", ".join(batch)}
        """
        client.execute(insert_sql)

    return table_name, len(rows)


def conform_to_silver(
    client: DatabricksSqlClient,
    catalog: str,
    bronze_schema: str,
    silver_schema: str,
    bronze_tables: list[str],
) -> None:
    for table_name in bronze_tables:
        sql = f"""
        CREATE OR REPLACE TABLE {catalog}.{silver_schema}.{table_name}
        USING DELTA
        AS
        SELECT *
        FROM {catalog}.{bronze_schema}.{table_name}
        """
        client.execute(sql)


def qualify_sql(sql_text: str, catalog: str, bronze_schema: str, silver_schema: str, gold_schema: str) -> str:
    """Qualify bare schema references (bronze., silver., gold.) with catalog prefix.

    Uses negative lookbehind to avoid double-qualifying references that already
    have the catalog prefix (e.g. ``dbw_ipai_dev.silver.`` stays unchanged).
    """
    escaped_catalog = re.escape(catalog)
    replacements = {
        rf"(?<!{escaped_catalog}\.)\bbronze\.": f"{catalog}.{bronze_schema}.",
        rf"(?<!{escaped_catalog}\.)\bsilver\.": f"{catalog}.{silver_schema}.",
        rf"(?<!{escaped_catalog}\.)\bgold\.": f"{catalog}.{gold_schema}.",
    }
    qualified = sql_text
    for pattern, replacement in replacements.items():
        qualified = re.sub(pattern, replacement, qualified)
    return qualified


def split_sql_statements(sql_text: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    in_single_quote = False

    for char in sql_text:
        if char == "'":
            in_single_quote = not in_single_quote
        if char == ";" and not in_single_quote:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(char)

    trailing = "".join(current).strip()
    if trailing:
        statements.append(trailing)
    return statements


def execute_gold_sql(
    client: DatabricksSqlClient,
    catalog: str,
    bronze_schema: str,
    silver_schema: str,
    gold_schema: str,
    gold_sql_dir: Path,
) -> list[str]:
    executed_files: list[str] = []
    for path in sorted(gold_sql_dir.glob("*.sql")):
        sql_text = qualify_sql(path.read_text(encoding="utf-8"), catalog, bronze_schema, silver_schema, gold_schema)
        for statement in split_sql_statements(sql_text):
            client.execute(statement)
        executed_files.append(path.name)
    return executed_files


def count_table_rows(client: DatabricksSqlClient, fq_table: str) -> int:
    value = client.query_scalar(f"SELECT COUNT(*) AS row_count FROM {fq_table}")
    return int(value)


def write_evidence(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    args = parse_args()

    client = DatabricksSqlClient(
        host=require(args.host, "DATABRICKS_HOST / --host"),
        token=require(args.token, "DATABRICKS_TOKEN / --token"),
        warehouse_id=require(args.warehouse_id, "DATABRICKS_WAREHOUSE_ID / --warehouse-id"),
    )

    seed_dir = Path(args.seed_dir)
    gold_sql_dir = Path(args.gold_sql_dir)

    if not seed_dir.exists():
        raise FileNotFoundError(f"Seed directory not found: {seed_dir}")
    if not gold_sql_dir.exists():
        raise FileNotFoundError(f"Gold SQL directory not found: {gold_sql_dir}")

    ensure_schemas(client, args.catalog, args.bronze_schema, args.silver_schema, args.gold_schema)

    loaded_tables: dict[str, int] = {}
    bronze_table_names: list[str] = []

    for csv_path in sorted(seed_dir.glob("*.csv")):
        table_name, row_count = load_bronze_table(client, args.catalog, args.bronze_schema, csv_path)
        loaded_tables[table_name] = row_count
        bronze_table_names.append(table_name)

    conform_to_silver(client, args.catalog, args.bronze_schema, args.silver_schema, bronze_table_names)
    executed_gold_files = execute_gold_sql(
        client=client,
        catalog=args.catalog,
        bronze_schema=args.bronze_schema,
        silver_schema=args.silver_schema,
        gold_schema=args.gold_schema,
        gold_sql_dir=gold_sql_dir,
    )

    gold_tables = [
        "project_profitability",
        "project_budget_vs_actual",
        "expense_liquidation_health",
        "ap_ar_cash_summary",
        "policy_compliance_scorecard",
        "portfolio_financial_health",
    ]

    evidence = {
        "catalog": args.catalog,
        "bronze_schema": args.bronze_schema,
        "silver_schema": args.silver_schema,
        "gold_schema": args.gold_schema,
        "loaded_bronze_tables": loaded_tables,
        "executed_gold_sql_files": executed_gold_files,
        "gold_row_counts": {
            table: count_table_rows(client, f"{args.catalog}.{args.gold_schema}.{table}")
            for table in gold_tables
        },
        "generated_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    write_evidence(Path(args.evidence_path), evidence)

    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
