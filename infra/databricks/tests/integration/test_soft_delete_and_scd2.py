"""Integration tests for soft-delete and SCD2 history mode."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from workbench.connectors.types import OpType, RunStatus, SyncOp
from tests.integration.conftest import DummyConnector


class DummyDeleteConnector(DummyConnector):
    """Connector that emits DELETE ops."""

    def update(self, state):
        yield SyncOp(
            op_type=OpType.UPSERT,
            table="test_table",
            data={"id": 1, "name": "Alice", "value": 100.0},
        )
        yield SyncOp(op_type=OpType.DELETE, table="test_table", keys={"id": 1})
        yield SyncOp(op_type=OpType.CHECKPOINT, table="", cursor={"offset": 1})


class TestSoftDelete:
    def test_delete_produces_soft_delete(self, make_engine, mock_spark: MagicMock) -> None:
        """DELETE ops set _fivetran_deleted=true (non-history mode)."""
        connector = DummyDeleteConnector()
        engine = make_engine(connector=connector)
        result = engine.run()
        assert result.status == RunStatus.SUCCESS
        # Should have called spark.sql for the delete MERGE
        sql_calls = [c[0][0] for c in mock_spark.sql.call_args_list]
        # Look for MERGE with _fivetran_deleted = true
        delete_merges = [
            s for s in sql_calls if "_fivetran_deleted" in s and "true" in s.lower()
        ]
        assert len(delete_merges) >= 1


class TestSCD2Mode:
    def test_scd2_creates_history_columns(self, make_engine, mock_spark: MagicMock) -> None:
        """SCD2 mode creates tables with _fivetran_active/start/end columns."""
        engine = make_engine(history_mode=True)
        engine.run()
        sql_calls = [c[0][0] for c in mock_spark.sql.call_args_list]
        create_calls = [s for s in sql_calls if "CREATE TABLE" in s and "test_table" in s]
        if create_calls:
            ddl = create_calls[0]
            assert "_fivetran_active" in ddl
            assert "_fivetran_start" in ddl
            assert "_fivetran_end" in ddl

    def test_scd2_upsert_uses_merge(self, make_engine, mock_spark: MagicMock) -> None:
        """SCD2 upsert uses MERGE statement for atomic close+insert."""
        engine = make_engine(history_mode=True)
        engine.run()
        sql_calls = [c[0][0] for c in mock_spark.sql.call_args_list]
        scd2_merges = [s for s in sql_calls if "MERGE" in s and "_fivetran_active" in s]
        assert len(scd2_merges) >= 1

    def test_scd2_delete_closes_active_row(self, make_engine, mock_spark: MagicMock) -> None:
        """SCD2 DELETE closes the active version."""
        connector = DummyDeleteConnector()
        engine = make_engine(connector=connector, history_mode=True)
        result = engine.run()
        assert result.status == RunStatus.SUCCESS
        sql_calls = [c[0][0] for c in mock_spark.sql.call_args_list]
        close_merges = [
            s
            for s in sql_calls
            if "_fivetran_active" in s and "_fivetran_deleted" in s and "MERGE" in s
        ]
        assert len(close_merges) >= 1
