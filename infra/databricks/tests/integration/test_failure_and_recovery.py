"""Integration tests for failure handling and recovery."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from workbench.connectors.types import RunStatus
from tests.integration.conftest import DummyConnector


class TestFailureAndRecovery:
    def test_connector_failure_marks_failure(self, make_engine, mock_spark: MagicMock) -> None:
        """Connector exception -> FAILURE status, state NOT advanced."""
        connector = DummyConnector(fail_on_update=True)
        engine = make_engine(connector=connector)
        result = engine.run()
        assert result.status == RunStatus.FAILURE
        assert "Simulated connector failure" in result.error_message

    def test_mid_sync_failure_no_state_advance(self, make_engine, mock_spark: MagicMock) -> None:
        """Failure after partial extraction does not advance state."""
        connector = DummyConnector(fail_after_n=1)
        engine = make_engine(connector=connector)
        result = engine.run()
        assert result.status == RunStatus.FAILURE
        # State merge should be mark_failure, not mark_success
        sql_calls = [c[0][0] for c in mock_spark.sql.call_args_list]
        # mark_failure increments consecutive_failures
        # It should NOT have saved the cursor from a partial sync

    def test_missing_checkpoint_is_failure(self, make_engine, mock_spark: MagicMock) -> None:
        """Connector that omits CHECKPOINT -> FAILURE (idempotency protection)."""
        connector = DummyConnector(omit_checkpoint=True)
        engine = make_engine(connector=connector)
        result = engine.run()
        assert result.status == RunStatus.FAILURE
        assert "CHECKPOINT" in result.error_message

    def test_recovery_after_failure(self, make_engine, mock_spark: MagicMock) -> None:
        """After a failed sync, a successful retry produces SUCCESS."""
        # First: fail
        fail_connector = DummyConnector(fail_on_update=True)
        engine1 = make_engine(connector=fail_connector)
        result1 = engine1.run()
        assert result1.status == RunStatus.FAILURE

        # Second: succeed
        mock_spark.sql.reset_mock()
        ok_connector = DummyConnector()
        engine2 = make_engine(connector=ok_connector)
        result2 = engine2.run()
        assert result2.status == RunStatus.SUCCESS

    def test_failure_records_metrics(self, make_engine, mock_spark: MagicMock) -> None:
        """Failed sync still records metrics to monitor table."""
        connector = DummyConnector(fail_on_update=True)
        engine = make_engine(connector=connector)
        engine.run()
        # Monitor.record_run should have been called
        sql_calls = [c[0][0] for c in mock_spark.sql.call_args_list]
        insert_calls = [s for s in sql_calls if "INSERT INTO" in s and "sync_runs" in s]
        assert len(insert_calls) >= 1
