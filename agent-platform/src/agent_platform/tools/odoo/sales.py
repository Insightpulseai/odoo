"""Odoo sales tool adapter — stub."""

from __future__ import annotations

from typing import Any

from agent_platform.tools.base import Tool, ToolResult
from agent_platform.tools.odoo.client import OdooClient


class OdooSalesTool(Tool):
    name = "odoo_sales"
    mutation = False
    approval_required = False

    def __init__(self) -> None:
        self._client = OdooClient()

    async def run(self, **kwargs: Any) -> ToolResult:
        partner_id: int | None = kwargs.get("partner_id")
        try:
            result = await self._client.call(
                "sale.order",
                "search_read",
                [[["partner_id", "=", partner_id]]],
                {"fields": ["name", "state", "amount_total"], "limit": 20},
            )
            return ToolResult(data=result)
        except Exception as exc:
            return ToolResult(data=None, error=str(exc))
