# -*- coding: utf-8 -*-
import logging
import time

from odoo import api, models

_logger = logging.getLogger(__name__)


class IpaiAiService(models.AbstractModel):
    _name = "ipai.ai.service"
    _description = "IPAI AI Service"

    @api.model
    def ask(self, prompt, thread_id=None, provider_id=None, context=None):
        """
        Send a prompt to the AI provider and persist the conversation.

        Args:
            prompt: The user's question/prompt
            thread_id: Optional existing thread ID for context
            provider_id: Optional provider ID (uses default if not specified)
            context: Optional dict with additional context

        Returns:
            dict with thread_id, answer, citations, latency_ms, etc.
        """
        # Get provider
        provider = (
            self.env["ipai.ai.provider"].browse(provider_id)
            if provider_id
            else self.env["ipai.ai.provider"].get_default()
        )
        if not provider:
            raise ValueError("No active AI provider configured.")

        # Ensure thread
        if thread_id:
            thread = self.env["ipai.ai.thread"].browse(thread_id)
            if not thread.exists():
                raise ValueError("Thread not found.")
        else:
            thread = self.env["ipai.ai.thread"].create({"provider_id": provider.id})

        # Persist user message
        user_msg = self.env["ipai.ai.message"].create(
            {
                "thread_id": thread.id,
                "role": "user",
                "content": prompt,
            }
        )

        # Call provider implementation
        impl = self._get_provider_impl(provider)
        t0 = time.time()
        try:
            resp = impl.call(
                prompt=prompt,
                external_thread_id=thread.external_thread_id,
                context=context,
            )
        except Exception as e:
            _logger.exception("AI provider call failed: %s", e)
            resp = {
                "status": "error",
                "answer": f"Provider error: {str(e)}",
                "citations": [],
                "confidence": 0.0,
            }
        dt = int((time.time() - t0) * 1000)

        # Normalize response
        answer = resp.get("answer") or ""
        external_thread_id = resp.get("external_thread_id")
        citations = resp.get("citations") or []
        confidence = float(resp.get("confidence") or 0.0)
        status = resp.get("status") or "ok"
        tokens = int(resp.get("tokens") or 0)

        # Update external thread ID if provided
        if external_thread_id and not thread.external_thread_id:
            thread.external_thread_id = external_thread_id

        # Persist assistant message
        asst_msg = self.env["ipai.ai.message"].create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": answer,
                "provider_latency_ms": dt,
                "provider_status": status,
                "confidence": confidence,
                "tokens_used": tokens,
            }
        )

        # Persist citations
        for i, c in enumerate(citations, start=1):
            self.env["ipai.ai.citation"].create(
                {
                    "message_id": asst_msg.id,
                    "rank": i,
                    "source_id": c.get("source_id"),
                    "title": c.get("title"),
                    "url": c.get("url"),
                    "snippet": c.get("snippet"),
                    "score": c.get("score"),
                }
            )

        # Update provider stats
        provider.update_stats(dt, tokens)

        _logger.info(
            "AI request: provider=%s thread=%s latency=%dms citations=%d",
            provider.name,
            thread.id,
            dt,
            len(citations),
        )

        return {
            "thread_id": thread.id,
            "external_thread_id": thread.external_thread_id,
            "user_message_id": user_msg.id,
            "assistant_message_id": asst_msg.id,
            "answer": answer,
            "citations": citations,
            "confidence": confidence,
            "latency_ms": dt,
            "status": status,
        }

    @api.model
    def _get_provider_impl(self, provider):
        """Get the provider implementation model based on provider_type."""
        impl_map = {
            "kapa": "ipai.ai.provider.kapa",
            "openai": "ipai.ai.provider.openai",
            "anthropic": "ipai.ai.provider.anthropic",
            "ollama": "ipai.ai.provider.ollama",
        }
        impl_name = impl_map.get(provider.provider_type)
        if not impl_name:
            raise ValueError(f"Unsupported provider type: {provider.provider_type}")
        if impl_name not in self.env:
            raise ValueError(f"Provider implementation not installed: {impl_name}")
        return self.env[impl_name]

    @api.model
    def get_thread_history(self, thread_id, limit=50):
        """Get conversation history for a thread."""
        messages = self.env["ipai.ai.message"].search(
            [("thread_id", "=", thread_id)],
            order="create_date asc",
            limit=limit,
        )
        return [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created": m.create_date.isoformat() if m.create_date else None,
                "citations": [
                    {
                        "title": c.title,
                        "url": c.url,
                        "snippet": c.snippet,
                        "score": c.score,
                    }
                    for c in m.citation_ids
                ],
            }
            for m in messages
        ]
