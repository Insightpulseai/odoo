"""Connector registry and factory.

Provides @register_connector decorator, create_connector() factory,
and list_connectors() discovery.
"""

from __future__ import annotations

import logging
from typing import Any

from workbench.connectors.base import BaseConnector

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, type[BaseConnector]] = {}


def register_connector(connector_id: str, name: str = "") -> Any:
    """Decorator to register a connector class in the global registry.

    Usage::

        @register_connector("notion", name="Notion")
        class NotionConnector(BaseConnector):
            ...
    """

    def decorator(cls: type[BaseConnector]) -> type[BaseConnector]:
        cls.connector_id = connector_id
        cls.connector_name = name or connector_id
        _REGISTRY[connector_id] = cls
        logger.debug("Registered connector: %s (%s)", connector_id, cls.__name__)
        return cls

    return decorator


def create_connector(connector_id: str, config: dict) -> BaseConnector:  # type: ignore[type-arg]
    """Factory: instantiate a connector by its registered ID.

    Args:
        connector_id: The registered connector identifier.
        config: Configuration dict passed to the connector constructor.

    Returns:
        An instance of the connector.

    Raises:
        KeyError: If the connector_id is not registered.
    """
    if connector_id not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise KeyError(
            f"Unknown connector '{connector_id}'. Available: {available}"
        )
    cls = _REGISTRY[connector_id]
    return cls(config)


def list_connectors() -> dict[str, str]:
    """Return a dict of registered connector_id -> connector_name."""
    return {cid: cls.connector_name for cid, cls in _REGISTRY.items()}
