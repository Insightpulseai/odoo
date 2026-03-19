"""Gold layer business mart builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyspark.sql import DataFrame
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

from workbench.config.logging import get_logger
from workbench.config.settings import get_settings

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = get_logger(__name__)


def build_budget_vs_actual(spark: SparkSession) -> DataFrame:
    """Build budget vs actual mart.

    Args:
        spark: Spark session

    Returns:
        Budget vs actual DataFrame
    """
    settings = get_settings()
    projects_table = settings.get_silver_path("notion_projects")
    budget_lines_table = settings.get_silver_path("notion_budget_lines")
    gold_table = settings.get_gold_path("ppm_budget_vs_actual")

    logger.info(f"Building {gold_table}")

    projects = spark.read.format("delta").table(projects_table)
    budget_lines = spark.read.format("delta").table(budget_lines_table)

    # Aggregate budget lines by project
    budget_agg = budget_lines.groupBy("project_id").agg(
        spark_sum(when(col("line_type") == "Budget", col("amount")).otherwise(0)).alias(
            "total_budget"
        ),
        spark_sum(when(col("line_type") == "Actual", col("amount")).otherwise(0)).alias(
            "total_actual"
        ),
        spark_sum(when(col("line_type") == "Forecast", col("amount")).otherwise(0)).alias(
            "total_forecast"
        ),
    )

    # Join with projects
    result = projects.join(budget_agg, "project_id", "left").select(
        col("project_id"),
        col("name").alias("project_name"),
        col("program_id"),
        col("status"),
        coalesce(col("total_budget"), lit(0)).alias("budget"),
        coalesce(col("total_actual"), lit(0)).alias("actual"),
        coalesce(col("total_forecast"), lit(0)).alias("forecast"),
        (coalesce(col("total_budget"), lit(0)) - coalesce(col("total_actual"), lit(0))).alias(
            "variance"
        ),
        when(
            col("total_budget") > 0,
            spark_round(col("total_actual") / col("total_budget") * 100, 2),
        )
        .otherwise(0)
        .alias("burn_rate_pct"),
        current_timestamp().alias("_etl_loaded_at"),
    )

    result.write.format("delta").mode("overwrite").saveAsTable(gold_table)
    logger.info(f"Built {result.count()} rows in {gold_table}")
    return result


def build_forecast(spark: SparkSession) -> DataFrame:
    """Build forecast mart with run-rate projections.

    Args:
        spark: Spark session

    Returns:
        Forecast DataFrame
    """
    settings = get_settings()
    budget_actual_table = settings.get_gold_path("ppm_budget_vs_actual")
    projects_table = settings.get_silver_path("notion_projects")
    gold_table = settings.get_gold_path("ppm_forecast")

    logger.info(f"Building {gold_table}")

    budget_actual = spark.read.format("delta").table(budget_actual_table)
    projects = spark.read.format("delta").table(projects_table)

    # Calculate run-rate forecast
    result = (
        budget_actual.join(
            projects.select("project_id", "start_date", "end_date"), "project_id", "left"
        )
        .withColumn(
            "run_rate_forecast",
            when(
                col("burn_rate_pct") > 0,
                spark_round(col("budget") * (col("burn_rate_pct") / 100) * 1.1, 2),
            ).otherwise(col("budget")),
        )
        .withColumn(
            "projected_variance",
            col("budget") - col("run_rate_forecast"),
        )
        .withColumn(
            "health_status",
            when(col("burn_rate_pct") > 100, "Over Budget")
            .when(col("burn_rate_pct") > 90, "At Risk")
            .when(col("burn_rate_pct") > 75, "On Track")
            .otherwise("Under Budget"),
        )
        .withColumn("_etl_loaded_at", current_timestamp())
    )

    result.write.format("delta").mode("overwrite").saveAsTable(gold_table)
    logger.info(f"Built {result.count()} rows in {gold_table}")
    return result


def build_risk_summary(spark: SparkSession) -> DataFrame:
    """Build risk summary mart.

    Args:
        spark: Spark session

    Returns:
        Risk summary DataFrame
    """
    settings = get_settings()
    risks_table = settings.get_silver_path("notion_risks")
    gold_table = settings.get_gold_path("ppm_risk_summary")

    logger.info(f"Building {gold_table}")

    risks = spark.read.format("delta").table(risks_table)

    # Aggregate risks by project
    result = risks.groupBy("project_id").agg(
        count("*").alias("total_risks"),
        count(when(col("status") == "Open", 1)).alias("open_risks"),
        count(when(col("severity") == "High", 1)).alias("high_severity"),
        count(when(col("severity") == "Medium", 1)).alias("medium_severity"),
        count(when(col("severity") == "Low", 1)).alias("low_severity"),
        count(when((col("severity") == "High") & (col("status") == "Open"), 1)).alias(
            "critical_open"
        ),
    )

    result = result.withColumn(
        "risk_score",
        (col("high_severity") * 3 + col("medium_severity") * 2 + col("low_severity") * 1),
    ).withColumn("_etl_loaded_at", current_timestamp())

    result.write.format("delta").mode("overwrite").saveAsTable(gold_table)
    logger.info(f"Built {result.count()} rows in {gold_table}")
    return result


def build_projects_summary(spark: SparkSession) -> DataFrame:
    """Build enriched projects summary mart.

    Args:
        spark: Spark session

    Returns:
        Projects summary DataFrame
    """
    settings = get_settings()
    budget_actual_table = settings.get_gold_path("ppm_budget_vs_actual")
    risk_summary_table = settings.get_gold_path("ppm_risk_summary")
    projects_table = settings.get_silver_path("notion_projects")
    programs_table = settings.get_silver_path("notion_programs")
    gold_table = settings.get_gold_path("ppm_projects_summary")

    logger.info(f"Building {gold_table}")

    projects = spark.read.format("delta").table(projects_table)
    programs = spark.read.format("delta").table(programs_table)
    budget_actual = spark.read.format("delta").table(budget_actual_table)
    risk_summary = spark.read.format("delta").table(risk_summary_table)

    # Join all dimensions
    result = (
        projects.join(
            programs.select(
                col("program_id"),
                col("name").alias("program_name"),
            ),
            "program_id",
            "left",
        )
        .join(
            budget_actual.select(
                "project_id",
                "budget",
                "actual",
                "variance",
                "burn_rate_pct",
            ),
            "project_id",
            "left",
        )
        .join(
            risk_summary.select(
                "project_id",
                "total_risks",
                "open_risks",
                "risk_score",
            ),
            "project_id",
            "left",
        )
        .withColumn(
            "overall_health",
            when(
                (col("burn_rate_pct") > 100) | (col("risk_score") > 10),
                "Critical",
            )
            .when(
                (col("burn_rate_pct") > 90) | (col("risk_score") > 5),
                "At Risk",
            )
            .otherwise("Healthy"),
        )
        .withColumn("_etl_loaded_at", current_timestamp())
    )

    result.write.format("delta").mode("overwrite").saveAsTable(gold_table)
    logger.info(f"Built {result.count()} rows in {gold_table}")
    return result
