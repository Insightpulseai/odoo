"""Connector SDK — Fivetran-equivalent data integration framework.

Provides BaseConnector ABC, connector registry, state management,
schema evolution, retry/rate-limiting, monitoring, and SyncEngine.
"""

from workbench.connectors.base import BaseConnector
from workbench.connectors.monitoring import SyncMonitor
from workbench.connectors.registry import create_connector, list_connectors, register_connector
from workbench.connectors.replay import ReplayEngine, ReplayMode, ReplayParams, ReplayResult
from workbench.connectors.schema_manager import SchemaManager
from workbench.connectors.state import StateManager
from workbench.connectors.sync_engine import SyncEngine
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

# Import connectors to trigger registration via @register_connector
from workbench.connectors.notion import NotionConnector  # noqa: F401
from workbench.connectors.azure import AzureConnector  # noqa: F401
from workbench.connectors.odoo_pg import OdooPgConnector  # noqa: F401
from workbench.connectors.github_api import GitHubConnector  # noqa: F401

__all__ = [
    # ABC
    "BaseConnector",
    # Registry
    "register_connector",
    "create_connector",
    "list_connectors",
    # Infrastructure
    "StateManager",
    "SchemaManager",
    "SyncMonitor",
    "SyncEngine",
    # Replay
    "ReplayEngine",
    "ReplayMode",
    "ReplayParams",
    "ReplayResult",
    # Types
    "ColumnDef",
    "ConnectorState",
    "OpType",
    "RunStatus",
    "SchemaPolicy",
    "SyncMode",
    "SyncOp",
    "SyncResult",
    "TableDef",
    # Connectors
    "NotionConnector",
    "AzureConnector",
    "OdooPgConnector",
    "GitHubConnector",
]
