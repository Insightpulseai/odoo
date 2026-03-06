"""Tests for BaseConnector ABC, types, and registry."""

from __future__ import annotations

from typing import Iterator
from unittest.mock import MagicMock

import pytest

from workbench.connectors.base import BaseConnector
from workbench.connectors.registry import (
    _REGISTRY,
    create_connector,
    list_connectors,
    register_connector,
)
from workbench.connectors.types import (
    ColumnDef,
    ConnectorState,
    OpType,
    RunStatus,
    SchemaPolicy,
    SyncMode,
    SyncOp,
    SyncResult,
    TableDef,
)


# ---------- Types tests ----------


class TestTypes:
    def test_sync_mode_values(self) -> None:
        assert SyncMode.INCREMENTAL.value == "incremental"
        assert SyncMode.FULL_REFRESH.value == "full_refresh"

    def test_schema_policy_values(self) -> None:
        assert SchemaPolicy.ALLOW_ALL.value == "allow_all"
        assert SchemaPolicy.ALLOW_COLUMNS.value == "allow_columns"
        assert SchemaPolicy.BLOCK_ALL.value == "block_all"

    def test_op_type_values(self) -> None:
        assert OpType.UPSERT.value == "upsert"
        assert OpType.DELETE.value == "delete"
        assert OpType.CHECKPOINT.value == "checkpoint"

    def test_column_def_frozen(self) -> None:
        col = ColumnDef("id", "LONG", nullable=False)
        assert col.name == "id"
        assert col.data_type == "LONG"
        assert col.nullable is False
        with pytest.raises(AttributeError):
            col.name = "other"  # type: ignore[misc]

    def test_table_def(self) -> None:
        cols = (ColumnDef("id", "LONG"), ColumnDef("name", "STRING"))
        td = TableDef(
            name="test_table",
            columns=cols,
            primary_key=("id",),
            sync_mode=SyncMode.INCREMENTAL,
        )
        assert td.name == "test_table"
        assert len(td.columns) == 2
        assert td.primary_key == ("id",)

    def test_sync_op(self) -> None:
        op = SyncOp(op_type=OpType.UPSERT, table="t", data={"id": 1, "val": "x"})
        assert op.op_type == OpType.UPSERT
        assert op.data["id"] == 1

    def test_connector_state_defaults(self) -> None:
        state = ConnectorState(connector_id="test")
        assert state.cursor == {}
        assert state.consecutive_failures == 0
        assert state.paused is False

    def test_sync_result_defaults(self) -> None:
        result = SyncResult(connector_id="test")
        assert result.status == RunStatus.RUNNING
        assert result.tables_synced == {}
        assert result.run_id  # UUID generated


# ---------- BaseConnector tests ----------


class DummyConnector(BaseConnector):
    """Minimal concrete connector for testing."""

    connector_id = "dummy"
    connector_name = "Dummy"

    def test_connection(self) -> bool:
        return True

    def schema(self) -> list[TableDef]:
        return [
            TableDef(
                name="dummy_table",
                columns=(ColumnDef("id", "LONG"),),
                primary_key=("id",),
            )
        ]

    def update(self, state: ConnectorState) -> Iterator[SyncOp]:
        yield SyncOp(op_type=OpType.UPSERT, table="dummy_table", data={"id": 1})
        yield SyncOp(op_type=OpType.CHECKPOINT, table="", cursor={"offset": 100})


class TestBaseConnector:
    def test_abstract_methods(self) -> None:
        """Cannot instantiate BaseConnector directly."""
        with pytest.raises(TypeError):
            BaseConnector({})  # type: ignore[abstract]

    def test_concrete_connector(self) -> None:
        conn = DummyConnector({"key": "val"})
        assert conn.test_connection() is True
        assert len(conn.schema()) == 1
        ops = list(conn.update(ConnectorState(connector_id="dummy")))
        assert len(ops) == 2
        assert ops[0].op_type == OpType.UPSERT
        assert ops[1].op_type == OpType.CHECKPOINT

    def test_context_manager(self) -> None:
        with DummyConnector({}) as conn:
            assert conn.test_connection() is True

    def test_config_stored(self) -> None:
        cfg = {"host": "localhost", "port": 5432}
        conn = DummyConnector(cfg)
        assert conn.config == cfg


# ---------- Registry tests ----------


class TestRegistry:
    def test_register_and_create(self) -> None:
        @register_connector("test_reg", name="Test Reg")
        class TestRegConnector(DummyConnector):
            pass

        assert "test_reg" in _REGISTRY
        conn = create_connector("test_reg", {})
        assert isinstance(conn, TestRegConnector)
        assert conn.connector_id == "test_reg"
        assert conn.connector_name == "Test Reg"

        # Cleanup
        del _REGISTRY["test_reg"]

    def test_create_unknown_raises(self) -> None:
        with pytest.raises(KeyError, match="Unknown connector"):
            create_connector("nonexistent", {})

    def test_list_connectors(self) -> None:
        connectors = list_connectors()
        assert isinstance(connectors, dict)
        # At minimum, notion and azure should be registered
        assert "notion" in connectors
        assert "azure" in connectors
