"""Delta-backed state manager for connector sync cursors.

Replaces ad-hoc watermark tracking with a unified MERGE-based
state table per connector.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from workbench.connectors.types import ConnectorState

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


class StateManager:
    """Manages connector state in a Delta table.

    Table: ``{catalog}.bronze.connector_state``
    One row per connector_id, MERGE-upserted on every sync.
    """

    def __init__(self, spark: SparkSession, catalog: str, schema: str = "bronze") -> None:
        self.spark = spark
        self.table = f"{catalog}.{schema}.connector_state"

    def ensure_table(self) -> None:
        """Create state table if it does not exist."""
        self.spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                connector_id        STRING NOT NULL,
                state_json          STRING NOT NULL,
                consecutive_failures INT NOT NULL,
                last_success        TIMESTAMP,
                last_failure        TIMESTAMP,
                paused              BOOLEAN NOT NULL,
                paused_reason       STRING,
                updated_at          TIMESTAMP NOT NULL
            )
            USING DELTA
            TBLPROPERTIES (
                'delta.enableChangeDataFeed' = 'true',
                'delta.autoOptimize.optimizeWrite' = 'true'
            )
        """)

    def get_state(self, connector_id: str) -> ConnectorState:
        """Load connector state from Delta. Returns empty state if not found."""
        try:
            rows = (
                self.spark.table(self.table)
                .filter(f"connector_id = '{connector_id}'")
                .collect()
            )
            if rows:
                row = rows[0]
                return ConnectorState(
                    connector_id=connector_id,
                    cursor=json.loads(row["state_json"] or "{}"),
                    consecutive_failures=row["consecutive_failures"],
                    last_success=row["last_success"],
                    last_failure=row["last_failure"],
                    paused=row["paused"],
                    paused_reason=row["paused_reason"] or "",
                    updated_at=row["updated_at"],
                )
        except Exception:
            logger.info("No existing state for %s, starting fresh", connector_id)

        return ConnectorState(connector_id=connector_id)

    def save_state(self, state: ConnectorState) -> None:
        """Persist connector state via MERGE INTO."""
        now = datetime.now(timezone.utc).isoformat()
        cursor_json = json.dumps(state.cursor)
        last_success = f"TIMESTAMP('{state.last_success.isoformat()}')" if state.last_success else "NULL"
        last_failure = f"TIMESTAMP('{state.last_failure.isoformat()}')" if state.last_failure else "NULL"

        self.spark.sql(f"""
            MERGE INTO {self.table} AS target
            USING (
                SELECT
                    '{state.connector_id}' AS connector_id,
                    '{cursor_json}' AS state_json,
                    {state.consecutive_failures} AS consecutive_failures,
                    {last_success} AS last_success,
                    {last_failure} AS last_failure,
                    {str(state.paused).lower()} AS paused,
                    '{state.paused_reason}' AS paused_reason,
                    TIMESTAMP('{now}') AS updated_at
            ) AS source
            ON target.connector_id = source.connector_id
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
        """)

    def mark_success(self, connector_id: str, cursor: dict) -> None:  # type: ignore[type-arg]
        """Record a successful sync run."""
        state = self.get_state(connector_id)
        state.cursor = cursor
        state.consecutive_failures = 0
        state.last_success = datetime.now(timezone.utc)
        state.paused = False
        state.paused_reason = ""
        self.save_state(state)
        logger.info("State saved for %s (success)", connector_id)

    def mark_failure(self, connector_id: str, error: str) -> None:
        """Record a failed sync run and increment failure counter."""
        state = self.get_state(connector_id)
        state.consecutive_failures += 1
        state.last_failure = datetime.now(timezone.utc)
        self.save_state(state)
        logger.warning(
            "State saved for %s (failure #%d): %s",
            connector_id,
            state.consecutive_failures,
            error,
        )

    def pause(self, connector_id: str, reason: str) -> None:
        """Pause a connector."""
        state = self.get_state(connector_id)
        state.paused = True
        state.paused_reason = reason
        self.save_state(state)
        logger.warning("Connector %s paused: %s", connector_id, reason)
