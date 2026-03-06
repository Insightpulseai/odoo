"""Replay engine for connector sync backfills and recovery.

Supports four modes:
- cursor: Resume from a specific cursor value
- time_range: Re-extract data within a time window
- full: Reset state, run full extraction
- dry_run: Collect ops without writing to Delta
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from workbench.connectors.base import BaseConnector
from workbench.connectors.state import StateManager
from workbench.connectors.sync_engine import SyncEngine
from workbench.connectors.types import (
    ConnectorState,
    OpType,
    RunStatus,
    SchemaPolicy,
    SyncOp,
    SyncResult,
)

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


class ReplayMode(str, Enum):
    """Replay execution modes."""

    CURSOR = "cursor"
    TIME_RANGE = "time_range"
    FULL = "full"
    DRY_RUN = "dry_run"


@dataclass
class ReplayParams:
    """Parameters for a replay execution."""

    mode: ReplayMode
    cursor: dict[str, Any] | None = None
    start_time: str | None = None
    end_time: str | None = None


@dataclass
class ReplayResult:
    """Result of a replay execution."""

    mode: ReplayMode
    connector_id: str
    sync_result: SyncResult | None = None
    ops_collected: int = 0
    ops_by_type: dict[str, int] = field(default_factory=dict)
    dry_run: bool = False
    error: str = ""

    @property
    def success(self) -> bool:
        if self.dry_run:
            return self.error == ""
        return self.sync_result is not None and self.sync_result.status == RunStatus.SUCCESS


class ReplayEngine:
    """Deterministic replay engine for connector syncs.

    Modes:
    - cursor: Override state.cursor with provided cursor, run SyncEngine
    - time_range: Set cursor to start time, run SyncEngine
    - full: Delete state for connector, run full SyncEngine
    - dry_run: Extract ops, count and log, skip writing to Delta
    """

    def __init__(
        self,
        spark: SparkSession,
        catalog: str,
        schema: str = "bronze",
        schema_policy: SchemaPolicy = SchemaPolicy.ALLOW_ALL,
        slack_webhook_url: str = "",
    ) -> None:
        self.spark = spark
        self.catalog = catalog
        self.schema = schema
        self.schema_policy = schema_policy
        self.slack_webhook_url = slack_webhook_url
        self.state_mgr = StateManager(spark, catalog, schema)

    def replay(
        self,
        connector: BaseConnector,
        params: ReplayParams,
    ) -> ReplayResult:
        """Execute a replay based on the given mode and parameters."""
        connector_id = connector.connector_id
        logger.info(
            "Starting replay for %s in mode=%s",
            connector_id,
            params.mode.value,
        )

        try:
            if params.mode == ReplayMode.DRY_RUN:
                return self._dry_run(connector, params)
            elif params.mode == ReplayMode.CURSOR:
                return self._replay_from_cursor(connector, params)
            elif params.mode == ReplayMode.TIME_RANGE:
                return self._replay_time_range(connector, params)
            elif params.mode == ReplayMode.FULL:
                return self._replay_full(connector, params)
            else:
                return ReplayResult(
                    mode=params.mode,
                    connector_id=connector_id,
                    error=f"Unknown replay mode: {params.mode}",
                )
        except Exception as e:
            logger.error("Replay failed for %s: %s", connector_id, e)
            return ReplayResult(
                mode=params.mode,
                connector_id=connector_id,
                error=str(e),
            )

    def _replay_from_cursor(
        self,
        connector: BaseConnector,
        params: ReplayParams,
    ) -> ReplayResult:
        """Override state cursor and run sync."""
        if params.cursor is None:
            return ReplayResult(
                mode=params.mode,
                connector_id=connector.connector_id,
                error="cursor parameter required for CURSOR mode",
            )

        # Override the saved state with the provided cursor
        state = self.state_mgr.get_state(connector.connector_id)
        state.cursor = params.cursor
        self.state_mgr.save_state(state)

        engine = self._create_engine(connector)
        sync_result = engine.run()

        return ReplayResult(
            mode=params.mode,
            connector_id=connector.connector_id,
            sync_result=sync_result,
        )

    def _replay_time_range(
        self,
        connector: BaseConnector,
        params: ReplayParams,
    ) -> ReplayResult:
        """Set cursor to start time and run sync."""
        if params.start_time is None:
            return ReplayResult(
                mode=params.mode,
                connector_id=connector.connector_id,
                error="start_time parameter required for TIME_RANGE mode",
            )

        # Build a cursor that represents "start from this time"
        # The exact cursor shape depends on the connector, so we use a generic approach
        time_cursor: dict[str, Any] = {"_replay_start": params.start_time}
        if params.end_time:
            time_cursor["_replay_end"] = params.end_time

        state = self.state_mgr.get_state(connector.connector_id)
        state.cursor = time_cursor
        self.state_mgr.save_state(state)

        engine = self._create_engine(connector)
        sync_result = engine.run()

        return ReplayResult(
            mode=params.mode,
            connector_id=connector.connector_id,
            sync_result=sync_result,
        )

    def _replay_full(
        self,
        connector: BaseConnector,
        params: ReplayParams,
    ) -> ReplayResult:
        """Reset state to empty and run full extraction."""
        connector_id = connector.connector_id
        logger.warning("Full replay for %s: resetting state to empty", connector_id)

        # Reset state to empty cursor
        empty_state = ConnectorState(connector_id=connector_id)
        self.state_mgr.save_state(empty_state)

        engine = self._create_engine(connector)
        sync_result = engine.run()

        return ReplayResult(
            mode=params.mode,
            connector_id=connector_id,
            sync_result=sync_result,
        )

    def _dry_run(
        self,
        connector: BaseConnector,
        params: ReplayParams,
    ) -> ReplayResult:
        """Extract ops but do not write to Delta. Log counts and types."""
        connector_id = connector.connector_id
        cursor = params.cursor or {}

        state = ConnectorState(connector_id=connector_id, cursor=cursor)
        ops = list(connector.update(state))

        ops_by_type: dict[str, int] = {}
        for op in ops:
            ops_by_type[op.op_type.value] = ops_by_type.get(op.op_type.value, 0) + 1

        logger.info(
            "Dry run for %s: %d ops — %s",
            connector_id,
            len(ops),
            json.dumps(ops_by_type),
        )

        return ReplayResult(
            mode=params.mode,
            connector_id=connector_id,
            ops_collected=len(ops),
            ops_by_type=ops_by_type,
            dry_run=True,
        )

    def _create_engine(self, connector: BaseConnector) -> SyncEngine:
        """Create a SyncEngine for the replay."""
        return SyncEngine(
            spark=self.spark,
            connector=connector,
            catalog=self.catalog,
            schema=self.schema,
            schema_policy=self.schema_policy,
            slack_webhook_url=self.slack_webhook_url,
        )
