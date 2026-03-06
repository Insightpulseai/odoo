"""Connector SDK type definitions.

Enums, dataclasses, and type aliases mirroring Fivetran's connector SDK.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SyncMode(str, Enum):
    """How the connector syncs data."""

    INCREMENTAL = "incremental"
    FULL_REFRESH = "full_refresh"


class SchemaPolicy(str, Enum):
    """How schema drift is handled."""

    ALLOW_ALL = "allow_all"
    ALLOW_COLUMNS = "allow_columns"
    BLOCK_ALL = "block_all"


class OpType(str, Enum):
    """Sync operation types."""

    UPSERT = "upsert"
    UPDATE = "update"
    DELETE = "delete"
    CHECKPOINT = "checkpoint"


class ConnectorStatus(str, Enum):
    """Connector lifecycle status."""

    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    SETUP = "setup"


class RunStatus(str, Enum):
    """Sync run status."""

    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ColumnDef:
    """Column definition in a connector's declared schema."""

    name: str
    data_type: str  # Spark SQL type: "STRING", "LONG", "TIMESTAMP", etc.
    nullable: bool = True
    description: str = ""


@dataclass(frozen=True)
class TableDef:
    """Table definition in a connector's declared schema."""

    name: str
    columns: tuple[ColumnDef, ...]
    primary_key: tuple[str, ...] = ()
    sync_mode: SyncMode = SyncMode.INCREMENTAL
    description: str = ""


@dataclass
class SyncOp:
    """A single sync operation emitted by a connector."""

    op_type: OpType
    table: str
    data: dict[str, Any] | None = None
    keys: dict[str, Any] | None = None
    cursor: dict[str, Any] | None = None


@dataclass
class ConnectorState:
    """Persisted state for a connector between sync runs."""

    connector_id: str
    cursor: dict[str, Any] = field(default_factory=dict)
    consecutive_failures: int = 0
    last_success: datetime | None = None
    last_failure: datetime | None = None
    paused: bool = False
    paused_reason: str = ""
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SyncResult:
    """Result of a sync run."""

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    connector_id: str = ""
    status: RunStatus = RunStatus.RUNNING
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    tables_synced: dict[str, int] = field(default_factory=dict)
    error_message: str = ""
    duration_seconds: float = 0.0
