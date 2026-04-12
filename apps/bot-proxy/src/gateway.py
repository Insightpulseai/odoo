"""
gateway.py — HTTP client that forwards bot activities to ipai-copilot-gateway.

Runs inside the ACA environment, reaches the gateway over the internal
DNS name. DefaultAzureCredential resolves the user-assigned MI attached
to this Container App.
"""

from __future__ import annotations

import json as _json
import logging
import os
from typing import Any, AsyncIterator

import aiohttp
from azure.identity.aio import DefaultAzureCredential

LOG = logging.getLogger("bot_proxy.gateway")

# Internal ACA FQDN (same env as the proxy). Not reachable from public
# internet — the proxy handles that external hop.
GATEWAY_URL = os.environ.get(
    "COPILOT_GATEWAY_URL",
    "http://ipai-copilot-gateway.internal.blackstone-0df78186.southeastasia.azurecontainerapps.io:8088",
)
GATEWAY_SCOPE = os.environ.get(
    "COPILOT_GATEWAY_SCOPE",
    "api://ipai-copilot-gateway/.default",
)


async def acquire_gateway_token() -> str:
    """Acquire MI token for the copilot gateway API (cached by Azure SDK)."""
    async with DefaultAzureCredential() as cred:
        token = await cred.get_token(GATEWAY_SCOPE)
        return token.token


async def stream_gateway(path: str, payload: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
    """POST payload to the gateway; yield NDJSON chunks as they arrive."""
    token = await acquire_gateway_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/x-ndjson",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.post(
                f"{GATEWAY_URL}{path}", json=payload, timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                resp.raise_for_status()
                async for line in resp.content:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield _json.loads(line)
                    except _json.JSONDecodeError:
                        LOG.warning("gateway.nonjson line: %r", line[:120])
                        continue
        except aiohttp.ClientError as err:
            LOG.exception("gateway.transport %s", err)
            raise
