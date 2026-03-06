# Databricks notebook source
"""Gold layer DLT placeholder.

This is a placeholder notebook for the silver-to-gold DLT pipeline.
Gold marts are currently built via regular Spark jobs (not DLT).
Replace this with actual DLT gold table definitions when migrating.
"""

import dlt
from pyspark.sql.functions import current_timestamp, lit


@dlt.table(
    name="gold_pipeline_status",
    comment="Pipeline health status placeholder",
)
def gold_pipeline_status():
    return spark.createDataFrame(  # noqa: F821
        [("silver_to_gold", "active")],
        ["pipeline", "status"],
    ).withColumn("updated_at", current_timestamp())
