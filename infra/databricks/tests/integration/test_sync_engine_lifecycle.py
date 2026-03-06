"""Integration tests for SyncEngine full lifecycle."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from workbench.connectors.types import RunStatus
from tests.integration.conftest import DummyConnector


class TestSyncEngineLifecycle:
    """Full lifecycle: state -> schema -> extract -> apply -> monitor."""

    def test_successful_sync(self, make_engine, mock_spark: MagicMock) -> None:
        """Normal sync: 2 upserts + checkpoint -> SUCCESS."""
        engine = make_engine()
        result = engine.run()
        assert result.status == RunStatus.SUCCESS
        assert result.tables_synced.get("test_table", 0) == 2
        assert result.duration_seconds >= 0
        assert result.error_message == ""

    def test_ensures_infrastructure_tables(self, make_engine, mock_spark: MagicMock) -> None:
        """SyncEngine creates state + monitor tables on run."""
        engine = make_engine()
        engine.run()
        # state_mgr.ensure_table and monitor.ensure_table should both be called
        # They call spark.sql with CREATE TABLE IF NOT EXISTS
        sql_calls = [c[0][0] for c in mock_spark.sql.call_args_list]
        create_calls = [s for s in sql_calls if "CREATE TABLE IF NOT EXISTS" in s]
        assert len(create_calls) >= 2  # state table + monitor table

    def test_schema_evolution_called(self, make_engine, mock_spark: MagicMock) -> None:
        """Schema tables are created/evolved during sync."""
        engine = make_engine()
        engine.run()
        # SchemaManager should have tried to create/check the test_table
        sql_calls = [c[0][0] for c in mock_spark.sql.call_args_list]
        # Should see CREATE TABLE for test_table (schema evolution)
        table_creates = [s for s in sql_calls if "test_table" in s and "CREATE" in s]
        assert len(table_creates) >= 1

    def test_state_persisted_on_success(self, make_engine, mock_spark: MagicMock) -> None:
        """mark_success is called with cursor from CHECKPOINT."""
        engine = make_engine()
        engine.run()
        # State save should produce a MERGE INTO connector_state
        sql_calls = [c[0][0] for c in mock_spark.sql.call_args_list]
        state_merges = [s for s in sql_calls if "connector_state" in s and "MERGE" in s]
        assert len(state_merges) >= 1

    def test_result_contains_run_id(self, make_engine) -> None:
        """SyncResult has a valid UUID run_id."""
        engine = make_engine()
        result = engine.run()
        assert len(result.run_id) == 36  # UUID format

    def test_paused_connector_skips_sync(self, make_engine, mock_spark: MagicMock) -> None:
        """Paused connector returns CANCELLED without extracting."""
        engine = make_engine()
        from workbench.connectors.types import ConnectorState

        paused_state = ConnectorState(
            connector_id="dummy",
            paused=True,
            paused_reason="Manual pause",
        )
        engine.state_mgr.get_state = MagicMock(return_value=paused_state)
        result = engine.run()
        assert result.status == RunStatus.CANCELLED
        assert "Paused" in result.error_message
