"""Bronze layer ingestion functions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from pyspark.sql import DataFrame
from pyspark.sql.functions import current_timestamp, lit

from workbench.config.logging import get_logger
from workbench.config.settings import get_settings
from workbench.connectors.azure import AzureConnector
from workbench.connectors.notion import NotionConnector

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = get_logger(__name__)


def ingest_notion_database(
    spark: SparkSession,
    database_id: str,
    table_name: str,
    filter_obj: dict[str, Any] | None = None,
) -> DataFrame:
    """Ingest a Notion database to bronze layer.

    Args:
        spark: Spark session
        database_id: Notion database ID
        table_name: Target table name (without schema)
        filter_obj: Optional Notion filter

    Returns:
        DataFrame with ingested data
    """
    settings = get_settings()
    bronze_table = settings.get_bronze_path(table_name)

    logger.info(f"Ingesting Notion database {database_id} to {bronze_table}")

    with NotionConnector() as connector:
        pages = connector.query_database(database_id, filter_obj)

    # Convert to DataFrame with raw JSON payload
    rows = [
        {
            "page_id": page["id"],
            "raw_json": json.dumps(page),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
        for page in pages
    ]

    df = spark.createDataFrame(rows)
    df = df.withColumn("_etl_loaded_at", current_timestamp())

    # Write to bronze table
    df.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(bronze_table)

    logger.info(f"Ingested {len(pages)} pages to {bronze_table}")
    return df


def ingest_azure_advisor(spark: SparkSession) -> DataFrame:
    """Ingest Azure Advisor recommendations to bronze layer.

    Args:
        spark: Spark session

    Returns:
        DataFrame with ingested data
    """
    settings = get_settings()
    bronze_table = settings.get_bronze_path("azure_advisor_raw")

    logger.info(f"Ingesting Azure Advisor recommendations to {bronze_table}")

    connector = AzureConnector()
    recommendations = connector.get_advisor_recommendations()

    # Convert to DataFrame with raw JSON
    rows = [
        {
            "recommendation_id": rec["id"],
            "raw_json": json.dumps(rec),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
        for rec in recommendations
    ]

    df = spark.createDataFrame(rows)
    df = df.withColumn("_etl_loaded_at", current_timestamp())

    # Write to bronze table
    df.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(
        bronze_table
    )

    logger.info(f"Ingested {len(recommendations)} recommendations to {bronze_table}")
    return df


def update_watermark(spark: SparkSession, source: str, last_sync: str) -> None:
    """Update sync watermark for incremental loads.

    .. deprecated:: Use SyncEngine + StateManager instead.

    Args:
        spark: Spark session
        source: Data source name
        last_sync: ISO timestamp of last successful sync
    """
    settings = get_settings()
    watermark_table = settings.get_bronze_path("sync_watermarks")

    df = spark.createDataFrame(
        [
            {
                "source": source,
                "last_sync": last_sync,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
    )

    df.write.format("delta").mode("append").saveAsTable(watermark_table)
    logger.info(f"Updated watermark for {source}: {last_sync}")


def ingest_via_sync_engine(
    spark: SparkSession,
    connector_id: str,
    config: dict[str, Any],
    slack_webhook_url: str = "",
    history_mode: bool = False,
) -> dict[str, Any]:
    """Run a connector sync via the SDK SyncEngine.

    This is the recommended entrypoint for new ingestion workflows.
    Replaces direct connector calls with full lifecycle management:
    state tracking, schema evolution, retry, monitoring, alerting.

    Args:
        spark: Spark session
        connector_id: Registered connector ID (notion, azure, odoo_pg, github)
        config: Connector-specific configuration dict
        slack_webhook_url: Optional Slack webhook for alerts
        history_mode: Enable SCD2 history tracking

    Returns:
        Dict with run_id, status, tables_synced, duration_seconds
    """
    from workbench.connectors import SyncEngine, create_connector

    settings = get_settings()
    connector = create_connector(connector_id, config)

    engine = SyncEngine(
        spark=spark,
        connector=connector,
        catalog=settings.catalog,
        schema=settings.schema_bronze,
        slack_webhook_url=slack_webhook_url,
        history_mode=history_mode,
    )

    try:
        result = engine.run()
        return {
            "run_id": result.run_id,
            "status": result.status.value,
            "tables_synced": result.tables_synced,
            "duration_seconds": result.duration_seconds,
            "error_message": result.error_message,
        }
    finally:
        connector.close()
