"""Integration tests for idempotent re-run behavior."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from workbench.connectors.types import ColumnDef, RunStatus, TableDef
from tests.integration.conftest import DummyConnector


class TestIdempotentRerun:
    def test_two_identical_runs_same_result(self, make_engine, mock_spark: MagicMock) -> None:
        """Running the same sync twice produces same RunStatus and table counts."""
        connector = DummyConnector()
        engine = make_engine(connector=connector)
        result1 = engine.run()
        assert result1.status == RunStatus.SUCCESS

        # Reset mock for second run
        mock_spark.sql.reset_mock()
        engine2 = make_engine(connector=DummyConnector())
        result2 = engine2.run()
        assert result2.status == RunStatus.SUCCESS
        assert result1.tables_synced == result2.tables_synced

    def test_deterministic_id_stable_across_runs(self) -> None:
        """_deterministic_id produces same hash for same PK data."""
        from workbench.connectors.sync_engine import SyncEngine

        engine = SyncEngine.__new__(SyncEngine)
        engine._table_defs = {
            "test": TableDef(
                name="test",
                columns=(ColumnDef("id", "LONG"), ColumnDef("name", "STRING")),
                primary_key=("id",),
            )
        }
        id1 = engine._deterministic_id("test", {"id": 42, "name": "Alice"})
        id2 = engine._deterministic_id("test", {"id": 42, "name": "Bob"})
        # Same PK -> same hash (name is mutable, not in PK)
        assert id1 == id2

    def test_deterministic_id_differs_for_different_pk(self) -> None:
        """_deterministic_id produces different hash for different PK."""
        from workbench.connectors.sync_engine import SyncEngine

        engine = SyncEngine.__new__(SyncEngine)
        engine._table_defs = {
            "test": TableDef(
                name="test",
                columns=(ColumnDef("id", "LONG"), ColumnDef("name", "STRING")),
                primary_key=("id",),
            )
        }
        id1 = engine._deterministic_id("test", {"id": 1, "name": "Alice"})
        id2 = engine._deterministic_id("test", {"id": 2, "name": "Alice"})
        assert id1 != id2

    def test_deterministic_id_fallback_no_pk(self) -> None:
        """Without PK, _deterministic_id hashes all data."""
        from workbench.connectors.sync_engine import SyncEngine

        engine = SyncEngine.__new__(SyncEngine)
        engine._table_defs = {
            "test": TableDef(
                name="test",
                columns=(ColumnDef("id", "LONG"), ColumnDef("name", "STRING")),
                primary_key=(),  # No PK
            )
        }
        id1 = engine._deterministic_id("test", {"id": 42, "name": "Alice"})
        id2 = engine._deterministic_id("test", {"id": 42, "name": "Bob"})
        # No PK -> full data hash -> different because name differs
        assert id1 != id2
