"""Tests for StateManager state read/write/failure tracking.

Since StateManager depends on SparkSession and Delta tables,
these tests mock the Spark layer.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from workbench.connectors.state import StateManager
from workbench.connectors.types import ConnectorState


@pytest.fixture
def mock_spark() -> MagicMock:
    """Create a mock SparkSession."""
    spark = MagicMock()
    return spark


@pytest.fixture
def state_mgr(mock_spark: MagicMock) -> StateManager:
    """Create a StateManager with mock Spark."""
    return StateManager(mock_spark, catalog="test_catalog", schema="bronze")


class TestStateManager:
    def test_table_name(self, state_mgr: StateManager) -> None:
        assert state_mgr.table == "test_catalog.bronze.connector_state"

    def test_ensure_table(self, state_mgr: StateManager, mock_spark: MagicMock) -> None:
        state_mgr.ensure_table()
        mock_spark.sql.assert_called_once()
        sql = mock_spark.sql.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS" in sql
        assert "test_catalog.bronze.connector_state" in sql

    def test_get_state_no_existing(self, state_mgr: StateManager, mock_spark: MagicMock) -> None:
        """Returns empty state when no row exists."""
        mock_spark.table.side_effect = Exception("Table not found")
        state = state_mgr.get_state("test_connector")
        assert state.connector_id == "test_connector"
        assert state.cursor == {}
        assert state.consecutive_failures == 0
        assert state.paused is False

    def test_get_state_existing(self, state_mgr: StateManager, mock_spark: MagicMock) -> None:
        """Returns populated state from existing row."""
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda self, key: {
            "state_json": '{"offset": 42}',
            "consecutive_failures": 3,
            "last_success": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "last_failure": datetime(2026, 1, 2, tzinfo=timezone.utc),
            "paused": False,
            "paused_reason": "",
            "updated_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
        }[key]

        mock_df = MagicMock()
        mock_df.filter.return_value = mock_df
        mock_df.collect.return_value = [mock_row]
        mock_spark.table.return_value = mock_df

        state = state_mgr.get_state("test_connector")
        assert state.connector_id == "test_connector"
        assert state.cursor == {"offset": 42}
        assert state.consecutive_failures == 3

    def test_save_state(self, state_mgr: StateManager, mock_spark: MagicMock) -> None:
        state = ConnectorState(
            connector_id="test",
            cursor={"page": 5},
            consecutive_failures=0,
        )
        state_mgr.save_state(state)
        mock_spark.sql.assert_called_once()
        sql = mock_spark.sql.call_args[0][0]
        assert "MERGE INTO" in sql
        assert "test_catalog.bronze.connector_state" in sql

    def test_mark_success(self, state_mgr: StateManager, mock_spark: MagicMock) -> None:
        # Mock get_state to return a state with failures
        mock_spark.table.side_effect = Exception("not found")
        state_mgr.mark_success("test", {"cursor_key": "val"})
        # Should have called sql for save_state (MERGE)
        assert mock_spark.sql.called

    def test_mark_failure(self, state_mgr: StateManager, mock_spark: MagicMock) -> None:
        mock_spark.table.side_effect = Exception("not found")
        state_mgr.mark_failure("test", "connection refused")
        assert mock_spark.sql.called

    def test_pause(self, state_mgr: StateManager, mock_spark: MagicMock) -> None:
        mock_spark.table.side_effect = Exception("not found")
        state_mgr.pause("test", "Auto-paused after 336 failures")
        assert mock_spark.sql.called
        sql = mock_spark.sql.call_args[0][0]
        assert "true" in sql.lower()  # paused = true
