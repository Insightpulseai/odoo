"""Rollup — Budget vs Actual (Silver → Gold).

Uses silver.budgets to produce monthly budget-vs-actual with cumulative
columns per project.

Usage::

    from ipai_data_intelligence.transforms.rollup_budget_actual import (
        build_budget_vs_actual,
    )
    build_budget_vs_actual(spark)
"""

from __future__ import annotations

from pyspark.sql import SparkSession, DataFrame, Window
from pyspark.sql.functions import (
    col,
    current_timestamp,
    round as spark_round,
    sum as spark_sum,
    when,
)

CATALOG = "dbw_ipai_dev"
SILVER = f"{CATALOG}.silver"
GOLD = f"{CATALOG}.gold"


def build_budget_vs_actual(spark: SparkSession) -> DataFrame:
    """Materialise ``gold.budget_vs_actual``.

    Columns produced:

    - ``project_id``, ``period``
    - ``planned_amount``, ``actual_amount``, ``variance``
    - ``cumulative_planned``, ``cumulative_actual``, ``cumulative_variance``
    - ``utilisation_pct`` — cumulative actual / cumulative planned
    - ``_loaded_at``
    """
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {GOLD}")

    budgets = spark.table(f"{SILVER}.budgets")

    window = (
        Window
        .partitionBy("project_id")
        .orderBy("period")
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )

    df = (
        budgets
        .withColumn("cumulative_planned", spark_sum("planned_amount").over(window))
        .withColumn("cumulative_actual", spark_sum("actual_amount").over(window))
        .withColumn(
            "cumulative_variance",
            col("cumulative_planned") - col("cumulative_actual"),
        )
        .withColumn(
            "utilisation_pct",
            when(
                col("cumulative_planned") > 0,
                spark_round(
                    col("cumulative_actual") / col("cumulative_planned") * 100, 2
                ),
            ),
        )
        .withColumn("_loaded_at", current_timestamp())
    )

    fqn = f"{GOLD}.budget_vs_actual"
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(fqn)
    )
    print(f"[rollup] {fqn}  ({df.count()} rows)")
    return df
