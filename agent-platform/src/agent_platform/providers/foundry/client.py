"""Foundry client factory — creates AzureAIAgentClient from settings."""

from __future__ import annotations

from agent_platform.logging import get_logger
from agent_platform.settings import Settings, get_settings

_logger = get_logger(__name__)


def create_foundry_client(settings: Settings | None = None) -> object:
    """
    Factory for azure.ai.agents.AzureAIAgentClient.

    Import is deferred so the package remains importable without azure-ai-agents
    installed (e.g. during unit tests that mock at the module boundary).
    """
    s = settings or get_settings()
    from agent_platform.providers.foundry.auth import get_foundry_token_provider

    try:
        from azure.ai.agents import AgentsClient  # type: ignore[import]

        client = AgentsClient(
            endpoint=s.foundry_endpoint,
            credential=get_foundry_token_provider(),  # type: ignore[arg-type]
        )
        _logger.info("foundry_client.created", endpoint=s.foundry_endpoint[:60])
        return client
    except ImportError:
        _logger.warning("foundry_client.sdk_missing")
        return None
