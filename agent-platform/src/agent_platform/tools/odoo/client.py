"""Odoo JSON-RPC client stub."""

from __future__ import annotations

import httpx

from agent_platform.logging import get_logger
from agent_platform.settings import get_settings

_logger = get_logger(__name__)


class OdooClient:
    def __init__(self) -> None:
        s = get_settings()
        self._base_url = s.odoo_url
        self._db = s.odoo_db
        self._api_key = s.odoo_api_key

    async def call(self, model: str, method: str, args: list, kwargs: dict) -> object:
        _logger.info("odoo.call", model=model, method=method)
        async with httpx.AsyncClient() as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": model,
                    "method": method,
                    "args": args,
                    "kwargs": kwargs,
                },
            }
            resp = await client.post(
                f"{self._base_url}/web/dataset/call_kw",
                json=payload,
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            resp.raise_for_status()
            return resp.json().get("result")
