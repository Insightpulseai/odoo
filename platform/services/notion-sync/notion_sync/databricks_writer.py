"""Write data to Databricks Delta tables."""

import json
import re
from datetime import datetime, timezone
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

    @staticmethod
    def _validate_identifier(name: str) -> str:
        """Validate a SQL identifier (catalog, schema, table name) against an allowlist pattern.

        Prevents SQL injection via malicious identifier names.
        Only allows alphanumeric characters and underscores, starting with a letter or underscore.

        Raises:
            ValueError: If the identifier contains disallowed characters.
        """
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
            raise ValueError(
                f"Invalid SQL identifier: {name!r}. "
                "Only letters, digits, and underscores are allowed, "
                "and it must start with a letter or underscore."
            )
        return name

    @staticmethod
    def _sanitize_sql_value(value: str, max_length: int = 1_000_000) -> str:
        """Sanitize a string value for safe interpolation into SQL literals.

        Rejects null bytes, escapes single quotes, and enforces a maximum length
        to prevent resource-exhaustion attacks.

        Raises:
            ValueError: If the value contains null bytes.
        """
        if "\x00" in value:
            raise ValueError("SQL value must not contain null bytes")
        value = value[:max_length]
        value = value.replace("'", "''")
        return value

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
        catalog = self._validate_identifier(self.config.catalog)
        schema = self._validate_identifier(self.config.schema_bronze)
        sql = f"""
        CREATE TABLE IF NOT EXISTS {catalog}.{schema}.notion_raw_pages (
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
        catalog = self._validate_identifier(self.config.catalog)
        # table_name may be "schema.table" — validate each part
        for part in table_name.split("."):
            self._validate_identifier(part)
        sql = f"""
        CREATE TABLE IF NOT EXISTS {catalog}.{table_name} (
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
        catalog = self._validate_identifier(self.config.catalog)
        for part in table_name.split("."):
            self._validate_identifier(part)
        safe_database_id = self._sanitize_sql_value(database_id)
        sql = f"""
        SELECT database_id, database_name, last_synced_at, last_edited_time, record_count
        FROM {catalog}.{table_name}
        WHERE database_id = '{safe_database_id}'
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
        catalog = self._validate_identifier(self.config.catalog)
        for part in table_name.split("."):
            self._validate_identifier(part)
        safe_database_id = self._sanitize_sql_value(database_id)
        safe_database_name = self._sanitize_sql_value(database_name)

        now = datetime.now(timezone.utc).isoformat()
        last_edited = last_edited_time.isoformat()

        # record_count is typed as int; enforce to prevent injection via crafted input
        safe_record_count = int(record_count)

        sql = f"""
        MERGE INTO {catalog}.{table_name} AS target
        USING (
            SELECT
                '{safe_database_id}' AS database_id,
                '{safe_database_name}' AS database_name,
                TIMESTAMP('{now}') AS last_synced_at,
                TIMESTAMP('{last_edited}') AS last_edited_time,
                {safe_record_count} AS record_count
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

        catalog = self._validate_identifier(self.config.catalog)
        schema = self._validate_identifier(self.config.schema_bronze)

        # Build VALUES clause
        values_parts = []
        for r in records:
            page_id = self._sanitize_sql_value(r.page_id)
            database_id = self._sanitize_sql_value(r.database_id)
            database_name = self._sanitize_sql_value(r.database_name)
            payload_escaped = self._sanitize_sql_value(r.payload)
            is_archived = "true" if r.is_archived else "false"
            values_parts.append(
                f"('{page_id}', '{database_id}', '{database_name}', "
                f"'{payload_escaped}', TIMESTAMP('{r.last_edited_time.isoformat()}'), "
                f"TIMESTAMP('{r.synced_at.isoformat()}'), {is_archived})"
            )

        values_sql = ",\n".join(values_parts)

        sql = f"""
        MERGE INTO {catalog}.{schema}.notion_raw_pages AS target
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

        catalog = self._validate_identifier(self.config.catalog)
        # table_name may be "schema.table" — validate each part
        for part in table_name.split("."):
            self._validate_identifier(part)

        # Get column names from first record — validate as identifiers
        columns = list(records[0].keys())
        for col in columns:
            self._validate_identifier(col)

        # Validate key_columns as identifiers
        for col in key_columns:
            self._validate_identifier(col)

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
                    val_escaped = self._sanitize_sql_value(str(val))
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

        full_table = f"{catalog}.{table_name}"

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
