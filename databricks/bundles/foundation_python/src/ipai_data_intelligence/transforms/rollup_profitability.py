"""Rollup — Project Profitability (Silver → Gold).

Joins silver.projects, silver.gl_journal_entries, and silver.invoices to
compute budget, actual cost, revenue, and margin per project.

Usage::

    from ipai_data_intelligence.transforms.rollup_profitability import (
        build_project_profitability,
    )
    build_project_profitability(spark)
"""

from __future__ import annotations

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    coalesce,
    col,
    current_timestamp,
    lit,
    round as spark_round,
    sum as spark_sum,
    when,
)

CATALOG = "dbw_ipai_dev"
SILVER = f"{CATALOG}.silver"
GOLD = f"{CATALOG}.gold"


def build_project_profitability(spark: SparkSession) -> DataFrame:
    """Materialise ``gold.project_profitability``.

    Columns produced:

    - ``project_id``, ``project_name``, ``cost_center``, ``status``
    - ``budget_amount`` — planned budget from silver.projects
    - ``total_cost`` — sum of GL debit entries typed ``cost``
    - ``total_revenue`` — sum of invoice amounts (paid + open)
    - ``gross_margin`` — revenue minus cost
    - ``margin_pct`` — gross_margin / revenue (null when revenue = 0)
    - ``budget_utilisation_pct`` — total_cost / budget_amount
    - ``_loaded_at``
    """
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {GOLD}")

    projects = spark.table(f"{SILVER}.projects").select(
        col("id").alias("project_id"),
        col("name").alias("project_name"),
        "cost_center",
        "status",
        "budget_amount",
    )

    # Cost = sum of debit on cost-type journal entries per project
    costs = (
        spark.table(f"{SILVER}.gl_journal_entries")
        .filter(col("entry_type") == "cost")
        .groupBy("project_id")
        .agg(spark_sum("debit").alias("total_cost"))
    )

    # Revenue = sum of invoice amounts per project
    revenue = (
        spark.table(f"{SILVER}.invoices")
        .groupBy("project_id")
        .agg(spark_sum("amount").alias("total_revenue"))
    )

    df = (
        projects
        .join(costs, "project_id", "left")
        .join(revenue, "project_id", "left")
        .withColumn("total_cost", coalesce(col("total_cost"), lit(0.0)))
        .withColumn("total_revenue", coalesce(col("total_revenue"), lit(0.0)))
        .withColumn("gross_margin", col("total_revenue") - col("total_cost"))
        .withColumn(
            "margin_pct",
            when(
                col("total_revenue") > 0,
                spark_round(col("gross_margin") / col("total_revenue") * 100, 2),
            ),
        )
        .withColumn(
            "budget_utilisation_pct",
            when(
                col("budget_amount") > 0,
                spark_round(col("total_cost") / col("budget_amount") * 100, 2),
            ),
        )
        .withColumn("_loaded_at", current_timestamp())
    )

    fqn = f"{GOLD}.project_profitability"
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(fqn)
    )
    print(f"[rollup] {fqn}  ({df.count()} rows)")
    return df
