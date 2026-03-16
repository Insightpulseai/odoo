"""Silver layer transformation functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col,
    current_timestamp,
    from_json,
    get_json_object,
    lit,
    to_date,
    to_timestamp,
    when,
)
from pyspark.sql.types import StringType, StructField, StructType

from workbench.config.logging import get_logger
from workbench.config.settings import get_settings

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = get_logger(__name__)


# Transformation registry for different table types
TRANSFORM_REGISTRY: dict[str, Callable[[DataFrame], DataFrame]] = {}


def register_transform(table_name: str) -> Callable:
    """Decorator to register a transformation function."""

    def decorator(func: Callable[[DataFrame], DataFrame]) -> Callable:
        TRANSFORM_REGISTRY[table_name] = func
        return func

    return decorator


@register_transform("programs")
def transform_programs(df: DataFrame) -> DataFrame:
    """Transform programs from Notion."""
    return df.select(
        get_json_object(col("raw_json"), "$.id").alias("program_id"),
        get_json_object(col("raw_json"), "$.properties.Name.title[0].plain_text").alias("name"),
        get_json_object(col("raw_json"), "$.properties.Status.select.name").alias("status"),
        get_json_object(col("raw_json"), "$.properties.Owner.people[0].name").alias("owner"),
        to_date(
            get_json_object(col("raw_json"), "$.properties.Start Date.date.start")
        ).alias("start_date"),
        to_date(
            get_json_object(col("raw_json"), "$.properties.End Date.date.start")
        ).alias("end_date"),
        get_json_object(col("raw_json"), "$.properties.Budget.number").cast("decimal(18,2)").alias(
            "budget"
        ),
        to_timestamp(get_json_object(col("raw_json"), "$.last_edited_time")).alias(
            "last_modified_at"
        ),
        current_timestamp().alias("_etl_loaded_at"),
    )


@register_transform("projects")
def transform_projects(df: DataFrame) -> DataFrame:
    """Transform projects from Notion."""
    return df.select(
        get_json_object(col("raw_json"), "$.id").alias("project_id"),
        get_json_object(col("raw_json"), "$.properties.Name.title[0].plain_text").alias("name"),
        get_json_object(col("raw_json"), "$.properties.Program.relation[0].id").alias("program_id"),
        get_json_object(col("raw_json"), "$.properties.Status.select.name").alias("status"),
        get_json_object(col("raw_json"), "$.properties.Priority.select.name").alias("priority"),
        get_json_object(col("raw_json"), "$.properties.Owner.people[0].name").alias("owner"),
        to_date(
            get_json_object(col("raw_json"), "$.properties.Start Date.date.start")
        ).alias("start_date"),
        to_date(
            get_json_object(col("raw_json"), "$.properties.End Date.date.start")
        ).alias("end_date"),
        get_json_object(col("raw_json"), "$.properties.Budget.number").cast("decimal(18,2)").alias(
            "budget"
        ),
        get_json_object(col("raw_json"), "$.properties.Actual.number").cast("decimal(18,2)").alias(
            "actual"
        ),
        to_timestamp(get_json_object(col("raw_json"), "$.last_edited_time")).alias(
            "last_modified_at"
        ),
        current_timestamp().alias("_etl_loaded_at"),
    )


@register_transform("budget_lines")
def transform_budget_lines(df: DataFrame) -> DataFrame:
    """Transform budget lines from Notion."""
    return df.select(
        get_json_object(col("raw_json"), "$.id").alias("budget_line_id"),
        get_json_object(col("raw_json"), "$.properties.Project.relation[0].id").alias("project_id"),
        get_json_object(col("raw_json"), "$.properties.Category.select.name").alias("category"),
        get_json_object(col("raw_json"), "$.properties.Description.rich_text[0].plain_text").alias(
            "description"
        ),
        get_json_object(col("raw_json"), "$.properties.Amount.number").cast("decimal(18,2)").alias(
            "amount"
        ),
        get_json_object(col("raw_json"), "$.properties.Type.select.name").alias("line_type"),
        to_date(get_json_object(col("raw_json"), "$.properties.Date.date.start")).alias(
            "line_date"
        ),
        current_timestamp().alias("_etl_loaded_at"),
    )


@register_transform("risks")
def transform_risks(df: DataFrame) -> DataFrame:
    """Transform risks from Notion."""
    return df.select(
        get_json_object(col("raw_json"), "$.id").alias("risk_id"),
        get_json_object(col("raw_json"), "$.properties.Project.relation[0].id").alias("project_id"),
        get_json_object(col("raw_json"), "$.properties.Name.title[0].plain_text").alias("name"),
        get_json_object(col("raw_json"), "$.properties.Category.select.name").alias("category"),
        get_json_object(col("raw_json"), "$.properties.Severity.select.name").alias("severity"),
        get_json_object(col("raw_json"), "$.properties.Probability.select.name").alias(
            "probability"
        ),
        get_json_object(col("raw_json"), "$.properties.Status.select.name").alias("status"),
        get_json_object(col("raw_json"), "$.properties.Mitigation.rich_text[0].plain_text").alias(
            "mitigation"
        ),
        to_timestamp(get_json_object(col("raw_json"), "$.last_edited_time")).alias(
            "last_modified_at"
        ),
        current_timestamp().alias("_etl_loaded_at"),
    )


def transform_notion_table(spark: SparkSession, table_name: str) -> DataFrame:
    """Transform a Notion table from bronze to silver.

    Args:
        spark: Spark session
        table_name: Name of the table to transform

    Returns:
        Transformed DataFrame
    """
    settings = get_settings()
    bronze_table = settings.get_bronze_path(f"notion_{table_name}_raw")
    silver_table = settings.get_silver_path(f"notion_{table_name}")

    logger.info(f"Transforming {bronze_table} -> {silver_table}")

    # Read bronze data
    bronze_df = spark.read.format("delta").table(bronze_table)

    # Apply registered transformation
    if table_name not in TRANSFORM_REGISTRY:
        raise ValueError(f"No transformation registered for table: {table_name}")

    transform_func = TRANSFORM_REGISTRY[table_name]
    silver_df = transform_func(bronze_df)

    # Write to silver
    silver_df.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(
        silver_table
    )

    logger.info(f"Transformed {silver_df.count()} rows to {silver_table}")
    return silver_df
