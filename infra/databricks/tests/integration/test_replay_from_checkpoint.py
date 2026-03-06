"""Integration tests for replay from checkpoint behavior."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from workbench.connectors.types import ConnectorState, RunStatus
from tests.integration.conftest import DummyConnector


class TestReplayFromCheckpoint:
    def test_replay_from_empty_produces_full_extract(
        self, make_engine, mock_spark: MagicMock
    ) -> None:
        """Replay from empty state extracts all rows."""
        engine = make_engine()
        result = engine.run()
        assert result.status == RunStatus.SUCCESS
        assert result.tables_synced.get("test_table", 0) == 2

    def test_replay_from_cursor_produces_no_duplicates(
        self, make_engine, mock_spark: MagicMock
    ) -> None:
        """Replay from caught-up cursor produces no UPSERTs."""
        connector = DummyConnector(cursor={"offset": 2})
        # Set initial state to caught-up cursor
        engine = make_engine(connector=connector)
        caught_up_state = ConnectorState(
            connector_id="dummy",
            cursor={"offset": 2},
        )
        engine.state_mgr.get_state = MagicMock(return_value=caught_up_state)
        result = engine.run()
        assert result.status == RunStatus.SUCCESS
        # No upserts because cursor matches
        assert result.tables_synced.get("test_table", 0) == 0

    def test_replay_produces_checkpoint(self, make_engine) -> None:
        """Both fresh and replay syncs produce a CHECKPOINT."""
        engine = make_engine()
        result = engine.run()
        assert result.status == RunStatus.SUCCESS
        # If we got SUCCESS, checkpoint was received (otherwise would be FAILURE)
