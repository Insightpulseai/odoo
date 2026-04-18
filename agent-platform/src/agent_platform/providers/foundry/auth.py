"""Foundry auth helpers — DefaultAzureCredential + bearer token provider."""

from __future__ import annotations

from typing import Callable

from azure.identity import DefaultAzureCredential, get_bearer_token_provider

_FOUNDRY_SCOPE = "https://ai.azure.com/.default"


def get_foundry_token_provider() -> Callable[[], str]:
    """Return a callable that yields a fresh bearer token for Azure AI Foundry."""
    credential = DefaultAzureCredential()
    return get_bearer_token_provider(credential, _FOUNDRY_SCOPE)
