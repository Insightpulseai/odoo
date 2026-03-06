"""Odoo PostgreSQL connector.

Incremental extraction from Odoo's PostgreSQL database using write_date
as the CDC cursor. Auto-discovers schema from information_schema.columns.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Iterator

from workbench.config.settings import get_settings
from workbench.connectors.base import BaseConnector
from workbench.connectors.registry import register_connector
from workbench.connectors.retry import RetryPolicy
from workbench.connectors.types import (
    ColumnDef,
    ConnectorState,
    OpType,
    SyncMode,
    SyncOp,
    TableDef,
)

logger = logging.getLogger(__name__)

# Odoo core tables to sync (all have write_date for CDC)
DEFAULT_TABLES = (
    "res_partner",
    "account_move",
    "account_move_line",
    "sale_order",
    "purchase_order",
    "product_product",
    "hr_employee",
    "project_project",
    "project_task",
)

# PostgreSQL -> Spark SQL type mapping
PG_TYPE_MAP: dict[str, str] = {
    "integer": "INT",
    "bigint": "LONG",
    "smallint": "SHORT",
    "numeric": "DECIMAL(20,6)",
    "double precision": "DOUBLE",
    "real": "FLOAT",
    "boolean": "BOOLEAN",
    "character varying": "STRING",
    "text": "STRING",
    "json": "STRING",
    "jsonb": "STRING",
    "date": "DATE",
    "timestamp without time zone": "TIMESTAMP",
    "timestamp with time zone": "TIMESTAMP",
    "bytea": "BINARY",
    "uuid": "STRING",
}

BATCH_SIZE = 10_000


@register_connector("odoo_pg", name="Odoo PostgreSQL")
class OdooPgConnector(BaseConnector):
    """Connector for Odoo PostgreSQL — incremental via write_date.

    Config keys:
        pg_host, pg_port, pg_database, pg_user, pg_password
        tables: list of table names (defaults to DEFAULT_TABLES)
    """

    retry_policy = RetryPolicy(
        max_retries=3,
        base_delay=2.0,
        retryable_exceptions=(Exception,),
    )
    rate_limit = 50.0  # Local DB, high throughput

    def __init__(self, config: dict) -> None:  # type: ignore[type-arg]
        super().__init__(config)
        settings = get_settings()
        self.pg_host = config.get("pg_host") or settings.odoo_pg_host
        self.pg_port = config.get("pg_port") or settings.odoo_pg_port
        self.pg_database = config.get("pg_database") or settings.odoo_pg_database
        self.pg_user = config.get("pg_user") or settings.odoo_pg_user
        self.pg_password = config.get("pg_password") or settings.odoo_pg_password
        self.tables: list[str] = list(config.get("tables", DEFAULT_TABLES))
        self._conn: Any = None

    def _get_conn(self) -> Any:
        if self._conn is None or self._conn.closed:
            import psycopg2

            self._conn = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                dbname=self.pg_database,
                user=self.pg_user,
                password=self.pg_password,
            )
        return self._conn

    def close(self) -> None:
        if self._conn and not self._conn.closed:
            self._conn.close()

    # ------------------------------------------------------------------
    # BaseConnector interface
    # ------------------------------------------------------------------

    def test_connection(self) -> bool:
        """Verify PostgreSQL connectivity."""
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone()[0] == 1

    def schema(self) -> list[TableDef]:
        """Auto-discover schema from information_schema.columns."""
        conn = self._get_conn()
        table_defs = []

        for table_name in self.tables:
            columns = self._discover_columns(conn, table_name)
            pk = self._discover_primary_key(conn, table_name)
            table_defs.append(
                TableDef(
                    name=f"odoo_{table_name}",
                    columns=tuple(columns),
                    primary_key=tuple(pk),
                    sync_mode=SyncMode.INCREMENTAL,
                    description=f"Odoo table: {table_name}",
                )
            )

        return table_defs

    def update(self, state: ConnectorState) -> Iterator[SyncOp]:
        """Extract rows incrementally using write_date cursor."""
        conn = self._get_conn()
        cursors: dict[str, str] = state.cursor.get("write_dates", {})

        for table_name in self.tables:
            since = cursors.get(table_name)
            max_write_date = since

            with conn.cursor() as cur:
                # Get column names
                cur.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'public' AND table_name = %s "
                    "ORDER BY ordinal_position",
                    (table_name,),
                )
                col_names = [row[0] for row in cur.fetchall()]

                # Build incremental query
                if since:
                    query = (
                        f'SELECT * FROM "{table_name}" '
                        f"WHERE write_date > %s ORDER BY write_date ASC"
                    )
                    cur.execute(query, (since,))
                else:
                    query = f'SELECT * FROM "{table_name}" ORDER BY write_date ASC'
                    cur.execute(query)

                # Batch fetch
                while True:
                    rows = cur.fetchmany(BATCH_SIZE)
                    if not rows:
                        break

                    for row in rows:
                        data: dict[str, Any] = {}
                        for col, val in zip(col_names, row):
                            data[col] = _serialize_value(val)

                        write_date = data.get("write_date", "")
                        if write_date and (not max_write_date or str(write_date) > str(max_write_date)):
                            max_write_date = str(write_date)

                        yield SyncOp(
                            op_type=OpType.UPSERT,
                            table=f"odoo_{table_name}",
                            data=data,
                        )

            if max_write_date:
                cursors[table_name] = max_write_date

            logger.info("Extracted from %s (since=%s)", table_name, since or "full")

        yield SyncOp(
            op_type=OpType.CHECKPOINT,
            table="",
            cursor={"write_dates": cursors},
        )

    # ------------------------------------------------------------------
    # Schema discovery
    # ------------------------------------------------------------------

    def _discover_columns(self, conn: Any, table_name: str) -> list[ColumnDef]:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
                """,
                (table_name,),
            )
            columns = []
            for col_name, data_type, is_nullable in cur.fetchall():
                spark_type = PG_TYPE_MAP.get(data_type, "STRING")
                columns.append(
                    ColumnDef(
                        name=col_name,
                        data_type=spark_type,
                        nullable=(is_nullable == "YES"),
                    )
                )
            return columns

    def _discover_primary_key(self, conn: Any, table_name: str) -> list[str]:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid
                    AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = %s::regclass AND i.indisprimary
                ORDER BY array_position(i.indkey, a.attnum)
                """,
                (table_name,),
            )
            return [row[0] for row in cur.fetchall()]


def _serialize_value(val: Any) -> Any:
    """Serialize a PostgreSQL value for JSON/Delta storage."""
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return json.dumps(val, default=str)
    if hasattr(val, "isoformat"):
        return val.isoformat()
    if isinstance(val, memoryview):
        return bytes(val).hex()
    if isinstance(val, bytes):
        return val.hex()
    return val
