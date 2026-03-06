"""Integration test fixtures.

Provides DummyConnector, mock Spark, and SyncEngine factory fixtures.
"""

from __future__ import annotations

from typing import Any, Iterator
from unittest.mock import MagicMock

import pytest

from workbench.connectors.base import BaseConnector
from workbench.connectors.retry import RetryPolicy
from workbench.connectors.types import (
    ColumnDef,
    ConnectorState,
    OpType,
    SchemaPolicy,
    SyncOp,
    TableDef,
)


class DummyConnector(BaseConnector):
    """Configurable test connector for integration tests.

    Behavior can be customized by setting:
    - _tables: list of TableDef to return from schema()
    - _rows: dict of table_name -> list of row dicts
    - _cursor: cursor dict to include in CHECKPOINT
    - _fail_on_update: if True, raises during update()
    - _fail_after_n: if set, fails after yielding N ops
    - _omit_checkpoint: if True, does not yield CHECKPOINT
    - _connection_ok: return value of test_connection()
    """

    connector_id = "dummy"
    connector_name = "Dummy"
    retry_policy = RetryPolicy(max_retries=0, base_delay=0.01, jitter=False)
    rate_limit = 1000.0

    def __init__(
        self,
        tables: list[TableDef] | None = None,
        rows: dict[str, list[dict[str, Any]]] | None = None,
        cursor: dict[str, Any] | None = None,
        fail_on_update: bool = False,
        fail_after_n: int | None = None,
        omit_checkpoint: bool = False,
        connection_ok: bool = True,
    ) -> None:
        self._tables = tables or [
            TableDef(
                name="test_table",
                columns=(
                    ColumnDef("id", "LONG", nullable=False),
                    ColumnDef("name", "STRING"),
                    ColumnDef("value", "DOUBLE"),
                ),
                primary_key=("id",),
            )
        ]
        self._rows = rows or {
            "test_table": [
                {"id": 1, "name": "Alice", "value": 100.0},
                {"id": 2, "name": "Bob", "value": 200.0},
            ]
        }
        self._cursor = cursor or {"offset": 2}
        self._fail_on_update = fail_on_update
        self._fail_after_n = fail_after_n
        self._omit_checkpoint = omit_checkpoint
        self._connection_ok = connection_ok
        self._closed = False
        super().__init__(config={})

    def test_connection(self) -> bool:
        return self._connection_ok

    def schema(self) -> list[TableDef]:
        return list(self._tables)

    def update(self, state: ConnectorState) -> Iterator[SyncOp]:
        if self._fail_on_update:
            raise RuntimeError("Simulated connector failure")

        count = 0
        for table_def in self._tables:
            table_name = table_def.name
            rows = self._rows.get(table_name, [])

            # If cursor matches, yield no rows (caught-up state)
            if state.cursor == self._cursor:
                continue

            for row in rows:
                if self._fail_after_n is not None and count >= self._fail_after_n:
                    raise RuntimeError(f"Simulated failure after {count} ops")
                yield SyncOp(op_type=OpType.UPSERT, table=table_name, data=dict(row))
                count += 1

        if not self._omit_checkpoint:
            yield SyncOp(op_type=OpType.CHECKPOINT, table="", cursor=dict(self._cursor))

    def close(self) -> None:
        self._closed = True


@pytest.fixture
def mock_spark() -> MagicMock:
    """Create a mock SparkSession with common behaviors."""
    spark = MagicMock()
    # Mock catalog for temp view cleanup
    spark.catalog = MagicMock()
    spark.catalog.dropTempView = MagicMock()
    # Mock createDataFrame to return a mock DF
    mock_df = MagicMock()
    mock_df.alias.return_value = mock_df
    spark.createDataFrame.return_value = mock_df
    # Mock spark.table for state/monitor table existence checks
    spark.table.side_effect = Exception("Table not found")
    return spark


@pytest.fixture
def dummy_connector() -> DummyConnector:
    """Default DummyConnector instance."""
    return DummyConnector()


@pytest.fixture
def make_engine(mock_spark: MagicMock):
    """Factory fixture: creates a SyncEngine with given connector and options."""
    from workbench.connectors.sync_engine import SyncEngine

    def _factory(
        connector: BaseConnector | None = None,
        catalog: str = "test_catalog",
        schema: str = "bronze",
        schema_policy: SchemaPolicy = SchemaPolicy.ALLOW_ALL,
        history_mode: bool = False,
    ) -> SyncEngine:
        conn = connector or DummyConnector()
        return SyncEngine(
            spark=mock_spark,
            connector=conn,
            catalog=catalog,
            schema=schema,
            schema_policy=schema_policy,
            history_mode=history_mode,
        )

    return _factory
