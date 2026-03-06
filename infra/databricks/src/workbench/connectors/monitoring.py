"""Sync run monitoring.

Writes per-run metrics to a Delta table for observability.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from workbench.connectors.types import RunStatus, SyncResult

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


class SyncMonitor:
    """Records sync run metrics to ``bronze.sync_runs`` Delta table."""

    def __init__(self, spark: SparkSession, catalog: str, schema: str = "bronze") -> None:
        self.spark = spark
        self.table = f"{catalog}.{schema}.sync_runs"

    def ensure_table(self) -> None:
        """Create sync_runs table if it does not exist."""
        self.spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                run_id           STRING NOT NULL,
                connector_id     STRING NOT NULL,
                status           STRING NOT NULL,
                started_at       TIMESTAMP NOT NULL,
                finished_at      TIMESTAMP,
                duration_seconds DOUBLE,
                tables_synced    MAP<STRING, LONG>,
                error_message    STRING
            )
            USING DELTA
            TBLPROPERTIES (
                'delta.enableChangeDataFeed' = 'true',
                'delta.autoOptimize.optimizeWrite' = 'true'
            )
        """)

    def record_run(self, result: SyncResult) -> None:
        """Write a completed sync run to the monitoring table."""
        finished = result.finished_at or datetime.now(timezone.utc)
        duration = result.duration_seconds or (finished - result.started_at).total_seconds()

        tables_map = ", ".join(
            f"'{k}', {v}L" for k, v in result.tables_synced.items()
        )
        tables_expr = f"MAP({tables_map})" if tables_map else "MAP()"

        error_escaped = (result.error_message or "").replace("'", "\\'")

        self.spark.sql(f"""
            INSERT INTO {self.table} VALUES (
                '{result.run_id}',
                '{result.connector_id}',
                '{result.status.value}',
                TIMESTAMP('{result.started_at.isoformat()}'),
                TIMESTAMP('{finished.isoformat()}'),
                {duration},
                {tables_expr},
                '{error_escaped}'
            )
        """)
        logger.info(
            "Recorded run %s for %s: %s (%.1fs, %d tables)",
            result.run_id,
            result.connector_id,
            result.status.value,
            duration,
            len(result.tables_synced),
        )

    def get_recent_runs(
        self, connector_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Fetch recent sync runs for a connector."""
        rows = (
            self.spark.table(self.table)
            .filter(f"connector_id = '{connector_id}'")
            .orderBy("started_at", ascending=False)
            .limit(limit)
            .collect()
        )
        return [row.asDict() for row in rows]
