"""Write data to Databricks Delta tables."""

import json
from datetime import datetime
from typing import Any

import structlog
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState

from .config import DatabricksConfig
from .models import BronzeRecord, SyncWatermark

logger = structlog.get_logger()


class DatabricksWriter:
    """Write data to Databricks Delta tables using SQL statements."""

    def __init__(self, config: DatabricksConfig):
        self.config = config
        self.client = WorkspaceClient(
            host=config.host,
            token=config.token,
        )
        self.warehouse_id = config.warehouse_id
        self.catalog = config.catalog
        self.logger = logger.bind(service="databricks-writer")

    def execute_sql(self, sql: str) -> dict[str, Any]:
        """Execute a SQL statement and wait for completion."""
        self.logger.debug("Executing SQL", sql=sql[:200])

        statement = self.client.statement_execution.execute_statement(
            warehouse_id=self.warehouse_id,
            catalog=self.catalog,
            statement=sql,
            wait_timeout="60s",
        )

        if statement.status.state == StatementState.FAILED:
            error_msg = statement.status.error.message if statement.status.error else "Unknown error"
            self.logger.error("SQL execution failed", error=error_msg)
            raise RuntimeError(f"SQL execution failed: {error_msg}")

        return {
            "status": statement.status.state.value,
            "row_count": statement.manifest.total_row_count if statement.manifest else 0,
        }

    def ensure_bronze_table(self) -> None:
        """Create bronze table if it doesn't exist."""
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.catalog}.{self.config.schema_bronze}.notion_raw_pages (
            page_id STRING,
            database_id STRING,
            database_name STRING,
            payload STRING,
            last_edited_time TIMESTAMP,
            synced_at TIMESTAMP,
            is_archived BOOLEAN
        )
        USING DELTA
        PARTITIONED BY (database_name)
        """
        self.execute_sql(sql)
        self.logger.info("Bronze table ensured")

    def ensure_watermark_table(self, table_name: str) -> None:
        """Create watermark table if it doesn't exist."""
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.catalog}.{table_name} (
            database_id STRING,
            database_name STRING,
            last_synced_at TIMESTAMP,
            last_edited_time TIMESTAMP,
            record_count BIGINT
        )
        USING DELTA
        """
        self.execute_sql(sql)
        self.logger.info("Watermark table ensured", table=table_name)

    def get_watermark(self, database_id: str, table_name: str) -> SyncWatermark | None:
        """Get the last sync watermark for a database."""
        sql = f"""
        SELECT database_id, database_name, last_synced_at, last_edited_time, record_count
        FROM {self.config.catalog}.{table_name}
        WHERE database_id = '{database_id}'
        ORDER BY last_synced_at DESC
        LIMIT 1
        """

        try:
            statement = self.client.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                catalog=self.catalog,
                statement=sql,
                wait_timeout="30s",
            )

            if statement.result and statement.result.data_array:
                row = statement.result.data_array[0]
                return SyncWatermark(
                    database_id=row[0],
                    database_name=row[1],
                    last_synced_at=datetime.fromisoformat(row[2]) if row[2] else datetime.min,
                    last_edited_time=datetime.fromisoformat(row[3]) if row[3] else datetime.min,
                    record_count=int(row[4]) if row[4] else 0,
                )
        except Exception as e:
            self.logger.warning("Failed to get watermark", error=str(e))

        return None

    def update_watermark(
        self,
        database_id: str,
        database_name: str,
        last_edited_time: datetime,
        record_count: int,
        table_name: str,
    ) -> None:
        """Update the sync watermark for a database."""
        now = datetime.utcnow().isoformat()
        last_edited = last_edited_time.isoformat()

        sql = f"""
        MERGE INTO {self.config.catalog}.{table_name} AS target
        USING (
            SELECT
                '{database_id}' AS database_id,
                '{database_name}' AS database_name,
                TIMESTAMP('{now}') AS last_synced_at,
                TIMESTAMP('{last_edited}') AS last_edited_time,
                {record_count} AS record_count
        ) AS source
        ON target.database_id = source.database_id
        WHEN MATCHED THEN UPDATE SET
            database_name = source.database_name,
            last_synced_at = source.last_synced_at,
            last_edited_time = source.last_edited_time,
            record_count = source.record_count
        WHEN NOT MATCHED THEN INSERT *
        """
        self.execute_sql(sql)
        self.logger.info(
            "Watermark updated",
            database_id=database_id,
            last_edited_time=last_edited,
            record_count=record_count,
        )

    def write_bronze_records(self, records: list[BronzeRecord]) -> int:
        """Write records to bronze table using MERGE."""
        if not records:
            return 0

        # Build VALUES clause
        values_parts = []
        for r in records:
            # Escape single quotes in payload
            payload_escaped = r.payload.replace("'", "''")
            values_parts.append(
                f"('{r.page_id}', '{r.database_id}', '{r.database_name}', "
                f"'{payload_escaped}', TIMESTAMP('{r.last_edited_time.isoformat()}'), "
                f"TIMESTAMP('{r.synced_at.isoformat()}'), {str(r.is_archived).lower()})"
            )

        values_sql = ",\n".join(values_parts)

        sql = f"""
        MERGE INTO {self.config.catalog}.{self.config.schema_bronze}.notion_raw_pages AS target
        USING (
            SELECT * FROM (
                VALUES {values_sql}
            ) AS t(page_id, database_id, database_name, payload, last_edited_time, synced_at, is_archived)
        ) AS source
        ON target.page_id = source.page_id AND target.database_id = source.database_id
        WHEN MATCHED THEN UPDATE SET
            payload = source.payload,
            last_edited_time = source.last_edited_time,
            synced_at = source.synced_at,
            is_archived = source.is_archived
        WHEN NOT MATCHED THEN INSERT *
        """

        result = self.execute_sql(sql)
        self.logger.info(
            "Bronze records written",
            count=len(records),
            database_name=records[0].database_name if records else None,
        )
        return len(records)

    def write_silver_records(
        self,
        table_name: str,
        records: list[dict[str, Any]],
        key_columns: list[str] = ["id"],
    ) -> int:
        """Write records to a silver table using MERGE."""
        if not records:
            return 0

        # Get column names from first record
        columns = list(records[0].keys())

        # Build VALUES clause
        values_parts = []
        for r in records:
            row_values = []
            for col in columns:
                val = r.get(col)
                if val is None:
                    row_values.append("NULL")
                elif isinstance(val, bool):
                    row_values.append(str(val).lower())
                elif isinstance(val, (int, float)):
                    row_values.append(str(val))
                elif isinstance(val, datetime):
                    row_values.append(f"TIMESTAMP('{val.isoformat()}')")
                else:
                    # Escape single quotes
                    val_escaped = str(val).replace("'", "''")
                    row_values.append(f"'{val_escaped}'")
            values_parts.append(f"({', '.join(row_values)})")

        values_sql = ",\n".join(values_parts)
        columns_sql = ", ".join(columns)

        # Build ON clause for key columns
        on_conditions = " AND ".join(
            f"target.{col} = source.{col}" for col in key_columns
        )

        # Build UPDATE SET clause (exclude key columns)
        update_cols = [c for c in columns if c not in key_columns]
        update_sql = ", ".join(f"{col} = source.{col}" for col in update_cols)

        full_table = f"{self.config.catalog}.{table_name}"

        sql = f"""
        MERGE INTO {full_table} AS target
        USING (
            SELECT * FROM (
                VALUES {values_sql}
            ) AS t({columns_sql})
        ) AS source
        ON {on_conditions}
        WHEN MATCHED THEN UPDATE SET {update_sql}
        WHEN NOT MATCHED THEN INSERT ({columns_sql}) VALUES ({', '.join(f'source.{c}' for c in columns)})
        """

        result = self.execute_sql(sql)
        self.logger.info("Silver records written", table=table_name, count=len(records))
        return len(records)

    def check_health(self) -> bool:
        """Check if Databricks is accessible."""
        try:
            self.execute_sql("SELECT 1")
            return True
        except Exception as e:
            self.logger.error("Databricks health check failed", error=str(e))
            return False
