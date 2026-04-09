"""Conform Finance — Bronze → Silver transforms.

Reads bronze seed tables, applies type casting, cleaning, and
conforming logic, then writes silver Delta tables.

Usage::

    from ipai_data_intelligence.transforms.conform_finance import conform_all
    conform_all(spark)
"""

from __future__ import annotations

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col,
    current_timestamp,
    to_date,
    trim,
    when,
)
from pyspark.sql.types import DoubleType, IntegerType

CATALOG = "dbw_ipai_dev"
BRONZE = f"{CATALOG}.bronze"
SILVER = f"{CATALOG}.silver"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_bronze(spark: SparkSession, table: str) -> DataFrame:
    return spark.table(f"{BRONZE}.{table}")


def _write_silver(df: DataFrame, table: str) -> None:
    fqn = f"{SILVER}.{table}"
    (
        df
        .withColumn("_loaded_at", current_timestamp())
        .write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(fqn)
    )
    print(f"[conform] {fqn}  ({df.count()} rows)")


# ---------------------------------------------------------------------------
# Individual conform functions
# ---------------------------------------------------------------------------

def conform_projects(spark: SparkSession) -> DataFrame:
    """bronze.seed_projects → silver.projects"""
    df = (
        _read_bronze(spark, "seed_projects")
        .withColumn("id", col("id").cast(IntegerType()))
        .withColumn("budget_amount", col("budget_amount").cast(DoubleType()))
        .withColumn("start_date", to_date(col("start_date")))
        .withColumn("end_date", to_date(col("end_date")))
        .withColumn("portfolio_id", col("portfolio_id").cast(IntegerType()))
        .withColumn("name", trim(col("name")))
    )
    _write_silver(df, "projects")
    return df


def conform_tasks(spark: SparkSession) -> DataFrame:
    """bronze.seed_tasks → silver.tasks"""
    df = (
        _read_bronze(spark, "seed_tasks")
        .withColumn("id", col("id").cast(IntegerType()))
        .withColumn("project_id", col("project_id").cast(IntegerType()))
        .withColumn("date_deadline", to_date(col("date_deadline")))
        .withColumn("create_date", to_date(col("create_date")))
        .withColumn("name", trim(col("name")))
    )
    _write_silver(df, "tasks")
    return df


def conform_employees(spark: SparkSession) -> DataFrame:
    """bronze.seed_employees → silver.employees"""
    df = (
        _read_bronze(spark, "seed_employees")
        .withColumn("cost_rate_daily", col("cost_rate_daily").cast(DoubleType()))
        .withColumn("name", trim(col("name")))
    )
    _write_silver(df, "employees")
    return df


def conform_gl_journal_entries(spark: SparkSession) -> DataFrame:
    """bronze.seed_gl_journal_entries → silver.gl_journal_entries"""
    df = (
        _read_bronze(spark, "seed_gl_journal_entries")
        .withColumn("date", to_date(col("date")))
        .withColumn("project_id", col("project_id").cast(IntegerType()))
        .withColumn("debit", col("debit").cast(DoubleType()))
        .withColumn("credit", col("credit").cast(DoubleType()))
        .withColumn("account_code", col("account_code").cast(IntegerType()))
    )
    _write_silver(df, "gl_journal_entries")
    return df


def conform_vendor_bills(spark: SparkSession) -> DataFrame:
    """bronze.seed_vendor_bills → silver.vendor_bills"""
    df = (
        _read_bronze(spark, "seed_vendor_bills")
        .withColumn("date", to_date(col("date")))
        .withColumn("due_date", to_date(col("due_date")))
        .withColumn("amount", col("amount").cast(DoubleType()))
        .withColumn("project_id", col("project_id").cast(IntegerType()))
    )
    _write_silver(df, "vendor_bills")
    return df


def conform_invoices(spark: SparkSession) -> DataFrame:
    """bronze.seed_invoices → silver.invoices"""
    df = (
        _read_bronze(spark, "seed_invoices")
        .withColumn("date", to_date(col("date")))
        .withColumn("due_date", to_date(col("due_date")))
        .withColumn("amount", col("amount").cast(DoubleType()))
        .withColumn("project_id", col("project_id").cast(IntegerType()))
    )
    _write_silver(df, "invoices")
    return df


def conform_payments(spark: SparkSession) -> DataFrame:
    """bronze.seed_payments → silver.payments"""
    df = (
        _read_bronze(spark, "seed_payments")
        .withColumn("date", to_date(col("date")))
        .withColumn("amount", col("amount").cast(DoubleType()))
        .withColumn("project_id", col("project_id").cast(IntegerType()))
    )
    _write_silver(df, "payments")
    return df


def conform_expenses(spark: SparkSession) -> DataFrame:
    """bronze.seed_expenses → silver.expenses"""
    df = (
        _read_bronze(spark, "seed_expenses")
        .withColumn("date", to_date(col("date")))
        .withColumn("amount", col("amount").cast(DoubleType()))
        .withColumn("project_id", col("project_id").cast(IntegerType()))
        .withColumn(
            "has_receipt",
            when(col("has_receipt") == "true", True).otherwise(False),
        )
        .withColumn(
            "policy_compliant",
            when(col("policy_compliant") == "true", True).otherwise(False),
        )
    )
    _write_silver(df, "expenses")
    return df


def conform_cash_advances(spark: SparkSession) -> DataFrame:
    """bronze.seed_cash_advances → silver.cash_advances"""
    df = (
        _read_bronze(spark, "seed_cash_advances")
        .withColumn("date", to_date(col("date")))
        .withColumn("amount", col("amount").cast(DoubleType()))
        .withColumn("liquidated_amount", col("liquidated_amount").cast(DoubleType()))
        .withColumn("project_id", col("project_id").cast(IntegerType()))
    )
    _write_silver(df, "cash_advances")
    return df


def conform_budgets(spark: SparkSession) -> DataFrame:
    """bronze.seed_budgets → silver.budgets"""
    df = (
        _read_bronze(spark, "seed_budgets")
        .withColumn("id", col("id").cast(IntegerType()))
        .withColumn("project_id", col("project_id").cast(IntegerType()))
        .withColumn("planned_amount", col("planned_amount").cast(DoubleType()))
        .withColumn("actual_amount", col("actual_amount").cast(DoubleType()))
        .withColumn("variance", col("variance").cast(DoubleType()))
    )
    _write_silver(df, "budgets")
    return df


def conform_portfolios(spark: SparkSession) -> DataFrame:
    """bronze.seed_portfolios → silver.portfolios"""
    df = (
        _read_bronze(spark, "seed_portfolios")
        .withColumn("id", col("id").cast(IntegerType()))
        .withColumn("name", trim(col("name")))
    )
    _write_silver(df, "portfolios")
    return df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def conform_all(spark: SparkSession) -> None:
    """Run all bronze → silver conform transforms."""
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SILVER}")

    conform_projects(spark)
    conform_tasks(spark)
    conform_employees(spark)
    conform_gl_journal_entries(spark)
    conform_vendor_bills(spark)
    conform_invoices(spark)
    conform_payments(spark)
    conform_expenses(spark)
    conform_cash_advances(spark)
    conform_budgets(spark)
    conform_portfolios(spark)

    print(f"[conform] Done — all silver tables written to {SILVER}")
