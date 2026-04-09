"""Rollup — Portfolio Health (Silver + Gold → Gold).

Joins gold.project_profitability, gold.expense_liquidation_health, and
silver.portfolios to produce a portfolio-level health scorecard.

Usage::

    from ipai_data_intelligence.transforms.rollup_portfolio import (
        build_portfolio_health,
    )
    build_portfolio_health(spark)

Note:
    This transform depends on gold.project_profitability and
    gold.expense_liquidation_health being materialised first.
"""

from __future__ import annotations

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    array_contains,
    coalesce,
    col,
    count,
    current_timestamp,
    explode,
    lit,
    round as spark_round,
    split,
    sum as spark_sum,
    when,
)
from pyspark.sql.types import IntegerType

CATALOG = "dbw_ipai_dev"
SILVER = f"{CATALOG}.silver"
GOLD = f"{CATALOG}.gold"


def build_portfolio_health(spark: SparkSession) -> DataFrame:
    """Materialise ``gold.portfolio_health``.

    Columns produced:

    - ``portfolio_id``, ``portfolio_name``, ``strategy``, ``owner``
    - ``project_count``
    - ``total_budget`` — sum of project budgets in portfolio
    - ``total_cost`` — sum of actual costs
    - ``total_revenue`` — sum of invoiced revenue
    - ``portfolio_margin`` — total_revenue - total_cost
    - ``portfolio_margin_pct``
    - ``avg_budget_utilisation_pct``
    - ``avg_compliance_rate_pct`` — average employee compliance in portfolio
    - ``avg_liquidation_rate_pct`` — average employee liquidation in portfolio
    - ``_loaded_at``
    """
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {GOLD}")

    # Explode portfolio project_ids into individual rows for joining
    portfolios = (
        spark.table(f"{SILVER}.portfolios")
        .withColumn("_project_id_str", explode(split(col("project_ids"), ",")))
        .withColumn(
            "project_id",
            col("_project_id_str").cast(IntegerType()),
        )
        .drop("_project_id_str")
    )

    profitability = spark.table(f"{GOLD}.project_profitability")

    # Join portfolios to project profitability
    portfolio_projects = (
        portfolios
        .join(profitability, "project_id", "inner")
    )

    # Aggregate at portfolio level
    portfolio_agg = (
        portfolio_projects
        .groupBy(
            col("id").alias("portfolio_id"),
            col("name").alias("portfolio_name"),
            "strategy",
            "owner",
        )
        .agg(
            count("project_id").alias("project_count"),
            spark_sum("budget_amount").alias("total_budget"),
            spark_sum("total_cost").alias("total_cost"),
            spark_sum("total_revenue").alias("total_revenue"),
        )
        .withColumn("portfolio_margin", col("total_revenue") - col("total_cost"))
        .withColumn(
            "portfolio_margin_pct",
            when(
                col("total_revenue") > 0,
                spark_round(
                    col("portfolio_margin") / col("total_revenue") * 100, 2
                ),
            ),
        )
        .withColumn(
            "avg_budget_utilisation_pct",
            when(
                col("total_budget") > 0,
                spark_round(col("total_cost") / col("total_budget") * 100, 2),
            ),
        )
    )

    # Expense health averages (portfolio-wide average of employee metrics)
    expense_health = spark.table(f"{GOLD}.expense_liquidation_health")
    expense_avg = expense_health.selectExpr(
        "avg(compliance_rate_pct) as avg_compliance_rate_pct",
        "avg(liquidation_rate_pct) as avg_liquidation_rate_pct",
    ).first()

    avg_compliance = float(expense_avg["avg_compliance_rate_pct"] or 0)
    avg_liquidation = float(expense_avg["avg_liquidation_rate_pct"] or 0)

    df = (
        portfolio_agg
        .withColumn("avg_compliance_rate_pct", lit(round(avg_compliance, 2)))
        .withColumn("avg_liquidation_rate_pct", lit(round(avg_liquidation, 2)))
        .withColumn("_loaded_at", current_timestamp())
    )

    fqn = f"{GOLD}.portfolio_health"
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(fqn)
    )
    print(f"[rollup] {fqn}  ({df.count()} rows)")
    return df
