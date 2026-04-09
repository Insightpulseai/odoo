"""Rollup — Expense Liquidation Health (Silver → Gold).

Joins silver.expenses and silver.cash_advances to compute per-employee
expense metrics including liquidation rates and policy compliance.

Usage::

    from ipai_data_intelligence.transforms.rollup_expense_health import (
        build_expense_liquidation_health,
    )
    build_expense_liquidation_health(spark)
"""

from __future__ import annotations

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    coalesce,
    col,
    count,
    current_timestamp,
    lit,
    round as spark_round,
    sum as spark_sum,
    when,
)

CATALOG = "dbw_ipai_dev"
SILVER = f"{CATALOG}.silver"
GOLD = f"{CATALOG}.gold"


def build_expense_liquidation_health(spark: SparkSession) -> DataFrame:
    """Materialise ``gold.expense_liquidation_health``.

    Columns produced:

    - ``employee_id``
    - ``total_expenses`` — count of expense records
    - ``total_expense_amount`` — sum of expense amounts
    - ``compliant_count`` — expenses where ``policy_compliant = true``
    - ``compliance_rate_pct``
    - ``receipts_attached_count`` — expenses with receipts
    - ``receipt_rate_pct``
    - ``total_advances`` — sum of cash advance amounts
    - ``total_liquidated`` — sum of liquidated amounts
    - ``liquidation_rate_pct``
    - ``unliquidated_balance``
    - ``_loaded_at``
    """
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {GOLD}")

    # Expense aggregates per employee
    expense_agg = (
        spark.table(f"{SILVER}.expenses")
        .groupBy("employee_id")
        .agg(
            count("*").alias("total_expenses"),
            spark_sum("amount").alias("total_expense_amount"),
            spark_sum(when(col("policy_compliant"), 1).otherwise(0)).alias(
                "compliant_count"
            ),
            spark_sum(when(col("has_receipt"), 1).otherwise(0)).alias(
                "receipts_attached_count"
            ),
        )
    )

    # Cash advance aggregates per employee
    advance_agg = (
        spark.table(f"{SILVER}.cash_advances")
        .groupBy("employee_id")
        .agg(
            spark_sum("amount").alias("total_advances"),
            spark_sum("liquidated_amount").alias("total_liquidated"),
        )
    )

    df = (
        expense_agg
        .join(advance_agg, "employee_id", "left")
        .withColumn("total_advances", coalesce(col("total_advances"), lit(0.0)))
        .withColumn("total_liquidated", coalesce(col("total_liquidated"), lit(0.0)))
        .withColumn(
            "compliance_rate_pct",
            when(
                col("total_expenses") > 0,
                spark_round(
                    col("compliant_count") / col("total_expenses") * 100, 2
                ),
            ),
        )
        .withColumn(
            "receipt_rate_pct",
            when(
                col("total_expenses") > 0,
                spark_round(
                    col("receipts_attached_count") / col("total_expenses") * 100, 2
                ),
            ),
        )
        .withColumn(
            "liquidation_rate_pct",
            when(
                col("total_advances") > 0,
                spark_round(
                    col("total_liquidated") / col("total_advances") * 100, 2
                ),
            ),
        )
        .withColumn(
            "unliquidated_balance",
            col("total_advances") - col("total_liquidated"),
        )
        .withColumn("_loaded_at", current_timestamp())
    )

    fqn = f"{GOLD}.expense_liquidation_health"
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(fqn)
    )
    print(f"[rollup] {fqn}  ({df.count()} rows)")
    return df
