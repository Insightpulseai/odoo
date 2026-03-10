"""Inherit llm.tool to emit bridge events on tool execution."""

import json
import logging
import uuid

from odoo import api, models

_logger = logging.getLogger(__name__)


class LlmTool(models.Model):
    _inherit = "llm.tool"

    def _execute(self, *args, **kwargs):
        """Wrap tool execution to emit pre/post events to Supabase."""
        idempotency_base = f"tool-{self.id}-{uuid.uuid4().hex[:12]}"
        bridge = self.env["ipai.bridge.event"]

        # Emit tool.call event (before execution)
        call_payload = {
            "tool_name": self.name,
            "tool_id": self.id,
            "args": _safe_serialize(args),
            "kwargs": _safe_serialize(kwargs),
            "user_id": self.env.uid,
            "user_login": self.env.user.login,
        }
        bridge._emit(
            event_type="tool.call",
            payload=call_payload,
            res_model="llm.tool",
            res_id=self.id,
            idempotency_key=f"{idempotency_base}-call",
        )

        # Execute the original tool
        result = super()._execute(*args, **kwargs)

        # Emit tool.result event (after execution)
        result_payload = {
            "tool_name": self.name,
            "tool_id": self.id,
            "result_preview": _safe_serialize(result)[:2000],
            "success": True,
            "user_id": self.env.uid,
        }
        bridge._emit(
            event_type="tool.result",
            payload=result_payload,
            res_model="llm.tool",
            res_id=self.id,
            idempotency_key=f"{idempotency_base}-result",
        )

        return result


def _safe_serialize(obj):
    """Best-effort JSON serialization, truncated for payload safety."""
    try:
        return json.dumps(obj, default=str)[:4000]
    except Exception:
        return str(obj)[:4000]
