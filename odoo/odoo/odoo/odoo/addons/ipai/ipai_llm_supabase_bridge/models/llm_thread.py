"""Inherit llm.thread to emit bridge events on thread lifecycle."""

import logging
import uuid

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LlmThread(models.Model):
    _inherit = "llm.thread"

    @api.model_create_multi
    def create(self, vals_list):
        """Emit thread.create event when a new thread is started."""
        threads = super().create(vals_list)
        bridge = self.env["ipai.bridge.event"]
        for thread in threads:
            bridge._emit(
                event_type="thread.create",
                payload={
                    "thread_id": thread.id,
                    "name": thread.name or "",
                    "assistant_id": getattr(thread, "assistant_id", False)
                    and thread.assistant_id.id,
                    "assistant_name": getattr(thread, "assistant_id", False)
                    and thread.assistant_id.name,
                    "user_id": self.env.uid,
                    "user_login": self.env.user.login,
                },
                res_model="llm.thread",
                res_id=thread.id,
                idempotency_key=f"thread-create-{thread.id}",
            )
        return threads

    def _generate(self, *args, **kwargs):
        """Wrap generation to emit start/complete events."""
        bridge = self.env["ipai.bridge.event"]
        run_key = uuid.uuid4().hex[:12]

        for thread in self:
            bridge._emit(
                event_type="generation.start",
                payload={
                    "thread_id": thread.id,
                    "thread_name": thread.name or "",
                    "user_id": self.env.uid,
                },
                res_model="llm.thread",
                res_id=thread.id,
                idempotency_key=f"gen-start-{thread.id}-{run_key}",
            )

        result = super()._generate(*args, **kwargs)

        for thread in self:
            bridge._emit(
                event_type="generation.complete",
                payload={
                    "thread_id": thread.id,
                    "thread_name": thread.name or "",
                    "user_id": self.env.uid,
                    "message_count": len(thread.message_ids)
                    if hasattr(thread, "message_ids")
                    else 0,
                },
                res_model="llm.thread",
                res_id=thread.id,
                idempotency_key=f"gen-complete-{thread.id}-{run_key}",
            )

        return result
