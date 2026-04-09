"""Rollup — Policy Compliance (Silver → Gold).

Uses silver.expenses to compute compliance rates segmented by policy
rule (receipt_required, amount_limit).

Usage::

    from ipai_data_intelligence.transforms.rollup_compliance import (
        build_policy_compliance,
    )
    build_policy_compliance(spark)
"""

from __future__ import annotations

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
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

# Policy thresholds (configurable)
RECEIPT_REQUIRED_THRESHOLD = 500.0  # receipt required for expenses >= this amount


def build_policy_compliance(spark: SparkSession) -> DataFrame:
    """Materialise ``gold.policy_compliance``.

    Produces one row per expense category with:

    - ``category``
    - ``total_expenses`` — count of expense records
    - ``total_amount``
    - ``receipt_required_count`` — expenses above receipt threshold
    - ``receipt_attached_count`` — of those, how many have receipts
    - ``receipt_compliance_pct``
    - ``policy_compliant_count`` — flagged compliant in source
    - ``policy_compliance_pct``
    - ``avg_expense_amount``
    - ``_loaded_at``
    """
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {GOLD}")

    expenses = spark.table(f"{SILVER}.expenses")

    df = (
        expenses
        .groupBy("category")
        .agg(
            count("*").alias("total_expenses"),
            spark_sum("amount").alias("total_amount"),
            # Receipt-required rule
            spark_sum(
                when(col("amount") >= RECEIPT_REQUIRED_THRESHOLD, 1).otherwise(0)
            ).alias("receipt_required_count"),
            spark_sum(
                when(
                    (col("amount") >= RECEIPT_REQUIRED_THRESHOLD) & col("has_receipt"),
                    1,
                ).otherwise(0)
            ).alias("receipt_attached_count"),
            # Policy compliance flag from source
            spark_sum(when(col("policy_compliant"), 1).otherwise(0)).alias(
                "policy_compliant_count"
            ),
        )
        .withColumn(
            "receipt_compliance_pct",
            when(
                col("receipt_required_count") > 0,
                spark_round(
                    col("receipt_attached_count")
                    / col("receipt_required_count")
                    * 100,
                    2,
                ),
            ).otherwise(lit(100.0)),
        )
        .withColumn(
            "policy_compliance_pct",
            when(
                col("total_expenses") > 0,
                spark_round(
                    col("policy_compliant_count") / col("total_expenses") * 100, 2
                ),
            ),
        )
        .withColumn(
            "avg_expense_amount",
            spark_round(col("total_amount") / col("total_expenses"), 2),
        )
        .withColumn("_loaded_at", current_timestamp())
    )

    fqn = f"{GOLD}.policy_compliance"
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(fqn)
    )
    print(f"[rollup] {fqn}  ({df.count()} rows)")
    return df
