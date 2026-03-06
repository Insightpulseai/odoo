"""Base connector abstract class.

All connectors extend BaseConnector and implement:
- test_connection(): Verify credentials and connectivity
- schema(): Declare tables and columns
- update(state): Extract data as a sequence of SyncOps
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Iterator

from workbench.connectors.retry import RetryPolicy
from workbench.connectors.types import ConnectorState, SyncOp, TableDef

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Abstract base for all connectors.

    Subclasses yield SyncOps; the SyncEngine writes them to Delta.
    Connectors never touch Spark/Delta directly.
    """

    connector_id: str = ""
    connector_name: str = ""
    retry_policy: RetryPolicy = RetryPolicy()
    rate_limit: float = 10.0  # requests per second

    def __init__(self, config: dict) -> None:  # type: ignore[type-arg]
        self.config = config

    @abstractmethod
    def test_connection(self) -> bool:
        """Verify credentials are valid and source is reachable."""
        ...

    @abstractmethod
    def schema(self) -> list[TableDef]:
        """Declare tables and columns this connector produces."""
        ...

    @abstractmethod
    def update(self, state: ConnectorState) -> Iterator[SyncOp]:
        """Extract data incrementally from the source.

        Uses state.cursor to resume from last position.
        Yields UPSERT/DELETE/CHECKPOINT ops.
        Final op should be CHECKPOINT with new cursor.
        """
        ...

    def close(self) -> None:
        """Release resources. Override if connector holds connections."""

    def __enter__(self) -> BaseConnector:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
