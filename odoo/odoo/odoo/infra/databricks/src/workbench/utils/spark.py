"""Spark session utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import SparkSession


def get_spark_session(app_name: str = "workbench") -> SparkSession:
    """Get or create a Spark session.

    In Databricks, this returns the existing session.
    In local development, creates a new session with Delta Lake support.

    Args:
        app_name: Application name for the Spark session

    Returns:
        SparkSession instance
    """
    from pyspark.sql import SparkSession

    # Check if running in Databricks
    try:
        from pyspark.dbutils import DBUtils

        # In Databricks, just get the existing session
        return SparkSession.builder.getOrCreate()
    except ImportError:
        # Local development - create session with Delta Lake
        return (
            SparkSession.builder.appName(app_name)
            .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.0.0")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config(
                "spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog",
            )
            .getOrCreate()
        )


def stop_spark_session() -> None:
    """Stop the active Spark session if it exists."""
    from pyspark.sql import SparkSession

    spark = SparkSession.getActiveSession()
    if spark:
        spark.stop()
