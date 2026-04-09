"""Silver layer: conform goal evidence from multiple sources.

Joins work items, specs, PR/build/deploy evidence, and agent run refs
into silver.goal_evidence_joined.

This is a stub — full implementation requires API connectors to
Azure Boards, GitHub, and Foundry which are wired in Phase 2.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    DoubleType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

GOAL_EVIDENCE_SCHEMA = StructType([
    StructField("evidence_id", StringType(), False),
    StructField("goal_id", StringType(), False),
    StructField("source_type", StringType(), False),
    StructField("source_ref_id", StringType(), False),
    StructField("source_url", StringType(), True),
    StructField("timestamp", TimestampType(), False),
    StructField("freshness_hours", DoubleType(), True),
    StructField("is_stale", BooleanType(), True),
    StructField("confidence", DoubleType(), True),
    StructField("summary", StringType(), True),
    StructField("derivation_method", StringType(), True),
])

FRESHNESS_THRESHOLD_HOURS = 48.0


def conform_goal_evidence(spark: SparkSession) -> DataFrame:
    """Conform goal evidence into silver.goal_evidence_joined.

    Phase 1: reads from bronze seed tables (CSV-loaded).
    Phase 2: reads from live API connectors (Azure Boards, GitHub, Foundry).
    """
    # Phase 1: empty dataframe with correct schema
    # Will be populated when API connectors are wired
    df = spark.createDataFrame([], GOAL_EVIDENCE_SCHEMA)

    # Compute freshness
    df = df.withColumn(
        "freshness_hours",
        (F.unix_timestamp(F.current_timestamp()) - F.unix_timestamp("timestamp")) / 3600.0,
    )
    df = df.withColumn(
        "is_stale",
        F.col("freshness_hours") > F.lit(FRESHNESS_THRESHOLD_HOURS),
    )

    return df


def write_silver_goal_evidence(spark: SparkSession) -> None:
    """Write conformed evidence to silver.goal_evidence_joined."""
    df = conform_goal_evidence(spark)
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable("silver.goal_evidence_joined")
    )
