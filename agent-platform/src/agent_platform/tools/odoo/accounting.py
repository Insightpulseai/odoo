"""Odoo accounting tool adapter — stub (mutation=True, approval required)."""

from __future__ import annotations

from typing import Any

from agent_platform.tools.base import Tool, ToolResult
from agent_platform.tools.odoo.client import OdooClient


class OdooAccountingTool(Tool):
    name = "odoo_accounting"
    mutation = True
    approval_required = True

    def __init__(self) -> None:
        self._client = OdooClient()

    async def run(self, **kwargs: Any) -> ToolResult:
        partner_id: int | None = kwargs.get("partner_id")
        try:
            result = await self._client.call(
                "account.move",
                "search_read",
                [[["partner_id", "=", partner_id], ["state", "=", "posted"]]],
                {"fields": ["name", "amount_residual", "invoice_date_due"], "limit": 20},
            )
            return ToolResult(data=result)
        except Exception as exc:
            return ToolResult(data=None, error=str(exc))
