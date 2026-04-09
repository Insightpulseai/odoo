"""Seed Loader — CSV → Bronze Delta Tables.

Reads CSV seed files from the lakeflow_ingestion seed directory and
materialises them as Delta tables in the ``bronze`` schema of the
``dbw_ipai_dev`` Unity Catalog.

Usage (Databricks notebook cell)::

    from ipai_data_intelligence.transforms.seed_loader import load_all_seeds
    load_all_seeds(spark)
"""

from __future__ import annotations

import os
from typing import Optional

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import current_timestamp, lit

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CATALOG = "dbw_ipai_dev"
SCHEMA = "bronze"

# Relative to this file's location inside the DAB bundle.
_DEFAULT_SEED_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..",  # up to bundles/
    "lakeflow_ingestion", "seed", "bronze",
)

# Mapping: CSV filename (without extension) → Delta table name.
SEED_TABLES: dict[str, str] = {
    "projects": "seed_projects",
    "tasks": "seed_tasks",
    "milestones": "seed_milestones",
    "employees": "seed_employees",
    "vendors": "seed_vendors",
    "customers": "seed_customers",
    "gl_journal_entries": "seed_gl_journal_entries",
    "vendor_bills": "seed_vendor_bills",
    "invoices": "seed_invoices",
    "payments": "seed_payments",
    "expenses": "seed_expenses",
    "expense_reports": "seed_expense_reports",
    "cash_advances": "seed_cash_advances",
    "budgets": "seed_budgets",
    "portfolios": "seed_portfolios",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_seed_path(seed_path: Optional[str] = None) -> str:
    """Return an absolute path to the seed CSV directory."""
    path = seed_path or _DEFAULT_SEED_PATH
    return os.path.abspath(path)


def _read_csv(spark: SparkSession, filepath: str) -> DataFrame:
    """Read a single CSV with header inference."""
    return (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .option("multiLine", "true")
        .csv(filepath)
        .withColumn("_loaded_at", current_timestamp())
    )


def _write_delta(df: DataFrame, table_fqn: str) -> None:
    """Overwrite a Delta table (CREATE OR REPLACE semantics)."""
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(table_fqn)
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_seed(
    spark: SparkSession,
    csv_name: str,
    table_name: str,
    seed_path: Optional[str] = None,
) -> DataFrame:
    """Load a single seed CSV into a bronze Delta table.

    Args:
        spark: Active SparkSession.
        csv_name: CSV filename without extension (e.g. ``"projects"``).
        table_name: Target Delta table name (e.g. ``"seed_projects"``).
        seed_path: Override directory containing CSV files.

    Returns:
        The DataFrame that was written.
    """
    base = _resolve_seed_path(seed_path)
    filepath = os.path.join(base, f"{csv_name}.csv")

    if not os.path.exists(filepath):
        print(f"[seed_loader] SKIP — file not found: {filepath}")
        return spark.createDataFrame([], schema="id STRING")

    df = _read_csv(spark, filepath)
    fqn = f"{CATALOG}.{SCHEMA}.{table_name}"
    _write_delta(df, fqn)
    print(f"[seed_loader] {fqn} ← {filepath}  ({df.count()} rows)")
    return df


def load_all_seeds(
    spark: SparkSession,
    seed_path: Optional[str] = None,
) -> dict[str, DataFrame]:
    """Load every registered seed CSV into its bronze Delta table.

    Args:
        spark: Active SparkSession.
        seed_path: Override directory containing CSV files.

    Returns:
        Dict mapping table name → DataFrame.
    """
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

    results: dict[str, DataFrame] = {}
    for csv_name, table_name in SEED_TABLES.items():
        df = load_seed(spark, csv_name, table_name, seed_path)
        results[table_name] = df

    print(f"[seed_loader] Done — {len(results)} tables loaded into {CATALOG}.{SCHEMA}")
    return results
