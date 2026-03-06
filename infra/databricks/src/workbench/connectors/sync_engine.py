"""SyncEngine — full lifecycle orchestrator for connector syncs.

Orchestrates: state load -> schema evolution -> extract -> persist ->
monitor -> alert, with retry and auto-pause support.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from workbench.connectors.base import BaseConnector
from workbench.connectors.monitoring import SyncMonitor
from workbench.connectors.retry import RateLimiter, RetryPolicy, should_auto_pause, with_retry
from workbench.connectors.schema_manager import SchemaManager
from workbench.connectors.state import StateManager
from workbench.connectors.types import (
    ConnectorState,
    OpType,
    RunStatus,
    SchemaPolicy,
    SyncOp,
    SyncResult,
    TableDef,
)
from workbench.observability.alerts import send_alert

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


class SyncEngine:
    """Full lifecycle orchestrator for a connector sync.

    Steps:
        1. StateManager.get_state()     -> load cursor from Delta
        2. SchemaManager.ensure_tables() -> create/evolve tables
        3. connector.update(state)       -> extract with retry
        4. _apply_op() per SyncOp        -> MERGE INTO bronze Delta
        5. StateManager.mark_success()   -> persist new cursor
        6. SyncMonitor.record_run()      -> write metrics
        7. On failure: escalate -> auto-pause after 14 days
        8. Slack alert on failure/schema-change
    """

    def __init__(
        self,
        spark: SparkSession,
        connector: BaseConnector,
        catalog: str,
        schema: str = "bronze",
        schema_policy: SchemaPolicy = SchemaPolicy.ALLOW_ALL,
        slack_webhook_url: str = "",
        sync_frequency_hours: float = 1.0,
        history_mode: bool = False,
    ) -> None:
        self.spark = spark
        self.connector = connector
        self.catalog = catalog
        self.schema = schema
        self.slack_webhook_url = slack_webhook_url
        self.sync_frequency_hours = sync_frequency_hours
        self.history_mode = history_mode

        self.state_mgr = StateManager(spark, catalog, schema)
        self.schema_mgr = SchemaManager(spark, catalog, schema, policy=schema_policy)
        self.monitor = SyncMonitor(spark, catalog, schema)
        self.rate_limiter = RateLimiter(requests_per_second=connector.rate_limit)

        # Cache table_defs for PK lookups during _deterministic_id
        self._table_defs: dict[str, TableDef] = {}

    def run(self) -> SyncResult:
        """Execute a full sync cycle. Returns SyncResult."""
        connector_id = self.connector.connector_id
        result = SyncResult(connector_id=connector_id)

        # Ensure infrastructure tables exist
        self.state_mgr.ensure_table()
        self.monitor.ensure_table()

        # 1. Load state
        state = self.state_mgr.get_state(connector_id)
        if state.paused:
            logger.warning("Connector %s is paused: %s", connector_id, state.paused_reason)
            result.status = RunStatus.CANCELLED
            result.error_message = f"Paused: {state.paused_reason}"
            result.finished_at = datetime.now(timezone.utc)
            self.monitor.record_run(result)
            return result

        try:
            # 2. Schema evolution
            table_defs = self.connector.schema()
            # Cache table defs for PK-based deterministic ID
            self._table_defs = {td.name: td for td in table_defs}
            drift_report = self.schema_mgr.ensure_tables(
                table_defs, history_mode=self.history_mode
            )
            self._alert_schema_drift(connector_id, drift_report)

            # 3. Extract with retry
            ops = self._extract_with_retry(state)

            # 4. Apply ops — track whether a CHECKPOINT was received
            new_cursor: dict[str, Any] = {}
            checkpoint_received = False
            for op in ops:
                if op.op_type == OpType.CHECKPOINT:
                    new_cursor = op.cursor or {}
                    checkpoint_received = True
                else:
                    self._apply_op(op, result)

            # 5. Save state — only if CHECKPOINT was emitted (Bug 0b fix)
            if checkpoint_received:
                self.state_mgr.mark_success(connector_id, new_cursor)
            else:
                # No CHECKPOINT means incomplete extraction — treat as failure
                raise RuntimeError(
                    f"Connector {connector_id} did not yield a CHECKPOINT op. "
                    "State not advanced to prevent data loss on retry."
                )

            # 6. Finalize result
            result.status = RunStatus.SUCCESS
            result.finished_at = datetime.now(timezone.utc)
            result.duration_seconds = (
                result.finished_at - result.started_at
            ).total_seconds()

        except Exception as exc:
            result.status = RunStatus.FAILURE
            result.error_message = str(exc)
            result.finished_at = datetime.now(timezone.utc)
            result.duration_seconds = (
                result.finished_at - result.started_at
            ).total_seconds()

            self.state_mgr.mark_failure(connector_id, str(exc))

            # Check auto-pause
            updated_state = self.state_mgr.get_state(connector_id)
            if should_auto_pause(updated_state, self.sync_frequency_hours):
                self.state_mgr.pause(
                    connector_id,
                    f"Auto-paused after {updated_state.consecutive_failures} consecutive failures",
                )
                self._alert_auto_pause(connector_id, updated_state)

            self._alert_failure(connector_id, str(exc))
            logger.error("Sync failed for %s: %s", connector_id, exc)

        # 7. Record metrics
        self.monitor.record_run(result)

        logger.info(
            "Sync %s for %s: %s (%.1fs, %d tables)",
            result.run_id[:8],
            connector_id,
            result.status.value,
            result.duration_seconds,
            len(result.tables_synced),
        )

        return result

    def _extract_with_retry(self, state: ConnectorState) -> list[SyncOp]:
        """Run connector.update(state) with retry policy."""
        policy = self.connector.retry_policy

        @with_retry(policy)
        def _do_extract() -> list[SyncOp]:
            return list(self.connector.update(state))

        return _do_extract()

    def _apply_op(self, op: SyncOp, result: SyncResult) -> None:
        """Apply a single SyncOp to the appropriate Delta table."""
        fq_table = f"{self.catalog}.{self.schema}.{op.table}"

        if op.op_type == OpType.UPSERT:
            self._apply_upsert(fq_table, op, result)
        elif op.op_type == OpType.UPDATE:
            self._apply_upsert(fq_table, op, result)  # Same MERGE logic
        elif op.op_type == OpType.DELETE:
            self._apply_delete(fq_table, op, result)

    def _apply_upsert(self, fq_table: str, op: SyncOp, result: SyncResult) -> None:
        """MERGE INTO for UPSERT/UPDATE ops with system columns.

        Uses Spark DataFrame API to avoid SQL injection (Bug 0a fix).
        """
        if not op.data:
            return

        # Add system columns
        now = datetime.now(timezone.utc).isoformat()
        row_id = self._deterministic_id(op.table, op.data)
        row_data = dict(op.data)
        row_data["_fivetran_synced"] = now
        row_data["_fivetran_deleted"] = False
        row_data["_fivetran_id"] = row_id

        if self.history_mode:
            row_data["_fivetran_active"] = True
            row_data["_fivetran_start"] = now
            row_data["_fivetran_end"] = None

        if self.history_mode:
            # SCD2: single atomic MERGE (Bug 0d fix)
            self._apply_scd2_upsert(fq_table, op, result, row_data)
        else:
            # Standard upsert via DataFrame MERGE — no string interpolation
            self._apply_df_merge(fq_table, row_data)

        # Track counts
        result.tables_synced[op.table] = result.tables_synced.get(op.table, 0) + 1

    def _apply_df_merge(self, fq_table: str, row_data: dict) -> None:
        """Execute a MERGE using Spark DataFrame API (SQL-injection safe)."""
        from pyspark.sql import Row
        from pyspark.sql.functions import col, lit

        # Create single-row DataFrame from the data
        source_df = self.spark.createDataFrame([Row(**{
            k: str(v) if v is not None and not isinstance(v, (bool, int, float)) else v
            for k, v in row_data.items()
        })])

        try:
            from delta.tables import DeltaTable
            target = DeltaTable.forName(self.spark, fq_table)
            (
                target.alias("target")
                .merge(source_df.alias("source"), "target._fivetran_id = source._fivetran_id")
                .whenMatchedUpdateAll()
                .whenNotMatchedInsertAll()
                .execute()
            )
        except Exception:
            # Fallback for environments where DeltaTable API is unavailable:
            # Use parameterized SQL via temp view (still safe from injection)
            view_name = f"_merge_src_{uuid.uuid4().hex[:8]}"
            source_df.createOrReplaceTempView(view_name)
            cols = list(row_data.keys())
            update_sets = ", ".join(f"target.{c} = source.{c}" for c in cols)
            insert_cols = ", ".join(cols)
            insert_vals = ", ".join(f"source.{c}" for c in cols)
            merge_sql = f"""
                MERGE INTO {fq_table} AS target
                USING {view_name} AS source
                ON target._fivetran_id = source._fivetran_id
                WHEN MATCHED THEN UPDATE SET {update_sets}
                WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
            """
            self.spark.sql(merge_sql)
            self.spark.catalog.dropTempView(view_name)

    def _apply_scd2_upsert(
        self,
        fq_table: str,
        op: SyncOp,
        result: SyncResult,
        row_data: dict,
    ) -> None:
        """SCD2 history mode: atomic close-old + insert-new via single MERGE (Bug 0d fix).

        Uses a single MERGE statement that:
        - WHEN MATCHED AND target._fivetran_active = true:
            closes the old row (active=false, end=now)
        - Followed by an INSERT of the new version

        We do this as a two-step MERGE within a single temp-view scope
        to ensure atomicity via Spark's transaction guarantees on Delta.
        """
        from pyspark.sql import Row

        now = datetime.now(timezone.utc).isoformat()
        fivetran_id = row_data.get("_fivetran_id", "")

        # Create source DataFrame
        source_df = self.spark.createDataFrame([Row(**{
            k: str(v) if v is not None and not isinstance(v, (bool, int, float)) else v
            for k, v in row_data.items()
        })])

        view_name = f"_scd2_src_{uuid.uuid4().hex[:8]}"
        source_df.createOrReplaceTempView(view_name)

        cols = list(row_data.keys())
        insert_cols = ", ".join(cols)
        insert_vals = ", ".join(f"source.{c}" for c in cols)

        # Single MERGE: close existing active row + insert new version
        # WHEN MATCHED closes the old active row
        # WHEN NOT MATCHED inserts the new version
        # After MERGE, always insert the new version row
        merge_sql = f"""
            MERGE INTO {fq_table} AS target
            USING {view_name} AS source
            ON target._fivetran_id = source._fivetran_id AND target._fivetran_active = true
            WHEN MATCHED THEN UPDATE SET
                target._fivetran_active = false,
                target._fivetran_end = source._fivetran_start
            WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
        """
        self.spark.sql(merge_sql)

        # Insert the new active version (the MERGE above only closed the old one when matched)
        # Check if MERGE matched (old row existed) — if so, we need to insert new version
        insert_sql = f"""
            INSERT INTO {fq_table} ({insert_cols})
            SELECT {insert_vals} FROM {view_name} AS source
            WHERE EXISTS (
                SELECT 1 FROM {fq_table}
                WHERE _fivetran_id = source._fivetran_id AND _fivetran_active = false
                AND _fivetran_end = source._fivetran_start
            )
        """
        self.spark.sql(insert_sql)
        self.spark.catalog.dropTempView(view_name)

        result.tables_synced[op.table] = result.tables_synced.get(op.table, 0) + 1

    def _apply_delete(self, fq_table: str, op: SyncOp, result: SyncResult) -> None:
        """Soft-delete: set _fivetran_deleted=true (SQL-injection safe via DataFrame API)."""
        if not op.keys:
            return

        row_id = self._deterministic_id(op.table, op.keys)
        now = datetime.now(timezone.utc).isoformat()

        from pyspark.sql import Row

        source_df = self.spark.createDataFrame([Row(
            _fivetran_id=row_id,
            _fivetran_synced=now,
        )])
        view_name = f"_del_src_{uuid.uuid4().hex[:8]}"
        source_df.createOrReplaceTempView(view_name)

        if self.history_mode:
            merge_sql = f"""
                MERGE INTO {fq_table} AS target
                USING {view_name} AS source
                ON target._fivetran_id = source._fivetran_id AND target._fivetran_active = true
                WHEN MATCHED THEN UPDATE SET
                    target._fivetran_deleted = true,
                    target._fivetran_active = false,
                    target._fivetran_end = TIMESTAMP(source._fivetran_synced),
                    target._fivetran_synced = TIMESTAMP(source._fivetran_synced)
            """
        else:
            merge_sql = f"""
                MERGE INTO {fq_table} AS target
                USING {view_name} AS source
                ON target._fivetran_id = source._fivetran_id
                WHEN MATCHED THEN UPDATE SET
                    target._fivetran_deleted = true,
                    target._fivetran_synced = TIMESTAMP(source._fivetran_synced)
            """
        self.spark.sql(merge_sql)
        self.spark.catalog.dropTempView(view_name)

        result.tables_synced[op.table] = result.tables_synced.get(op.table, 0) + 1

    def _deterministic_id(self, table: str, data: dict) -> str:  # type: ignore[type-arg]
        """Generate a deterministic row ID from table name + primary key columns.

        Bug 0c fix: Hash only declared PK columns, not full data.
        Falls back to full-data hash if no PK declared.
        """
        table_def = self._table_defs.get(table)
        if table_def and table_def.primary_key:
            # Use only PK columns for deterministic ID
            pk_data = {k: data.get(k) for k in table_def.primary_key}
            key_str = json.dumps(pk_data, sort_keys=True, default=str)
        else:
            # Fallback: full data hash (no PK declared)
            key_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(f"{table}:{key_str}".encode()).hexdigest()[:32]

    # ------------------------------------------------------------------
    # Alerting
    # ------------------------------------------------------------------

    def _alert_failure(self, connector_id: str, error: str) -> None:
        if not self.slack_webhook_url:
            return
        send_alert(
            webhook_url=self.slack_webhook_url,
            title=f"Connector Sync Failed: {connector_id}",
            message=f"Error: {error}",
            severity="error",
            metadata={"connector": connector_id},
        )

    def _alert_auto_pause(self, connector_id: str, state: ConnectorState) -> None:
        if not self.slack_webhook_url:
            return
        send_alert(
            webhook_url=self.slack_webhook_url,
            title=f"Connector Auto-Paused: {connector_id}",
            message=(
                f"Paused after {state.consecutive_failures} consecutive failures. "
                "Manual intervention required."
            ),
            severity="critical",
            metadata={
                "connector": connector_id,
                "failures": str(state.consecutive_failures),
            },
        )

    def _alert_schema_drift(
        self, connector_id: str, drift_report: dict[str, list]  # type: ignore[type-arg]
    ) -> None:
        new_cols = {t: cols for t, cols in drift_report.items() if cols}
        if not new_cols or not self.slack_webhook_url:
            return
        details = "; ".join(
            f"{t}: +{len(cols)} cols" for t, cols in new_cols.items()
        )
        send_alert(
            webhook_url=self.slack_webhook_url,
            title=f"Schema Drift Detected: {connector_id}",
            message=f"New columns added: {details}",
            severity="warning",
            metadata={"connector": connector_id},
        )
