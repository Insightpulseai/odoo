"""
bot.py — PulserBot: Bot Framework activity handler that proxies to
`ipai-copilot-gateway` and streams the response back to Teams / Copilot.

Streaming contract (see docs/skills/m365-copilot-streaming-contract.md):
  * ONE StreamingResponse per user turn
  * call endStream() before sending any other activity
  * media via setAttachments() INSIDE the stream, not as separate activity
  * serialize outgoing messages — no parallel sends
"""

from __future__ import annotations

import logging
import os
from typing import Any

import aiohttp
from azure.identity.aio import DefaultAzureCredential
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.core.streaming import StreamingResponse  # type: ignore[import-not-found]
from botbuilder.schema import ChannelAccount

LOG = logging.getLogger("pulser.bot")

GATEWAY_URL = os.environ.get(
    "COPILOT_GATEWAY_URL",
    "https://ipai-copilot-gateway.insightpulseai.com",
)
GATEWAY_SCOPE = os.environ.get(
    "COPILOT_GATEWAY_SCOPE",
    # default to the gateway's own app registration — the ACA app exposes
    # an API with this audience when running with MI auth.
    "api://ipai-copilot-gateway/.default",
)


class PulserBot(ActivityHandler):
    async def on_members_added_activity(
        self,
        members_added: list[ChannelAccount],
        turn_context: TurnContext,
    ) -> None:
        for member in members_added:
            if member.id == turn_context.activity.recipient.id:
                continue
            await turn_context.send_activity(
                "Hi — I'm Pulser. Ask me about Odoo, BIR, or Azure."
                " Try: `/odoo what modules are installed?` or just a question."
            )

    async def on_message_activity(self, turn_context: TurnContext) -> None:
        user_text = (turn_context.activity.text or "").strip()
        if not user_text:
            return

        # Open ONE streaming response per turn — do not interleave sends.
        stream = StreamingResponse(turn_context)
        try:
            await stream.queue_informative_update("Thinking…")

            async for chunk in self._call_gateway(
                user_text,
                user_id=turn_context.activity.from_property.aad_object_id,
            ):
                text = chunk.get("text")
                if text:
                    await stream.queue_text_chunk(text)

                attachments = chunk.get("attachments")
                if attachments:
                    # Attach media INSIDE the stream, not as a separate activity.
                    stream.set_attachments(attachments)

        except Exception as err:
            LOG.exception("gateway.error %s", err)
            await stream.queue_text_chunk(
                "\n\n_Pulser backend error — try again in a moment._"
            )
        finally:
            # Always end the stream before any subsequent activity.
            await stream.end_stream()

    async def _call_gateway(
        self,
        prompt: str,
        user_id: str | None,
    ) -> Any:
        """Stream NDJSON chunks from ipai-copilot-gateway."""
        token = await self._acquire_gateway_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/x-ndjson",
        }
        payload = {
            "prompt": prompt,
            "user_id": user_id,
            "surface": "teams",
            "stream": True,
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(
                f"{GATEWAY_URL}/chat", json=payload, timeout=60
            ) as resp:
                resp.raise_for_status()
                async for line in resp.content:
                    line = line.strip()
                    if not line:
                        continue
                    # NDJSON: each line is one chunk
                    import json as _json

                    yield _json.loads(line)

    async def _acquire_gateway_token(self) -> str:
        """Acquire MI token for the copilot gateway API."""
        async with DefaultAzureCredential() as cred:
            token = await cred.get_token(GATEWAY_SCOPE)
            return token.token
