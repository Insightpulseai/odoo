"""
finance-close-surface/bot/bot.py — Monthly Close orchestrator persona.

Maker-Checker pattern: close / reopen actions require approval — the
gateway enforces the gate based on the caller's Entra scopes.
"""

from __future__ import annotations

import json as _json
import logging
import os

import aiohttp
from azure.identity.aio import DefaultAzureCredential
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.core.streaming import StreamingResponse  # type: ignore[import-not-found]
from botbuilder.schema import ChannelAccount

LOG = logging.getLogger("finance_close.bot")

AGENT_NAME = "finance-close"
SURFACE_TAG = "teams-finance-close"

GATEWAY_URL = os.environ.get(
    "COPILOT_GATEWAY_URL",
    "https://ipai-copilot-gateway.insightpulseai.com",
)
GATEWAY_SCOPE = os.environ.get(
    "COPILOT_GATEWAY_SCOPE",
    "api://ipai-copilot-gateway/.default",
)

WELCOME = (
    "Finance Close ready. I orchestrate your monthly close — checklist, status, "
    "variance review, and period lock.\n\n"
    "Try `/status`, `/checklist`, `/close`, `/variance`, or `/reopen`."
)


class FinanceCloseBot(ActivityHandler):
    async def on_members_added_activity(
        self,
        members_added: list[ChannelAccount],
        turn_context: TurnContext,
    ) -> None:
        for member in members_added:
            if member.id == turn_context.activity.recipient.id:
                continue
            await turn_context.send_activity(WELCOME)

    async def on_message_activity(self, turn_context: TurnContext) -> None:
        user_text = (turn_context.activity.text or "").strip()
        if not user_text:
            return

        stream = StreamingResponse(turn_context)
        try:
            await stream.queue_informative_update("Checking close state…")

            async for chunk in self._call_gateway(
                prompt=user_text,
                user_id=turn_context.activity.from_property.aad_object_id,
            ):
                text = chunk.get("text")
                if text:
                    await stream.queue_text_chunk(text)
                if chunk.get("attachments"):
                    stream.set_attachments(chunk["attachments"])

        except Exception as err:
            LOG.exception("gateway.error %s", err)
            await stream.queue_text_chunk(
                "\n\n_Finance Close backend error — try again in a moment._"
            )
        finally:
            await stream.end_stream()

    async def _call_gateway(self, prompt: str, user_id: str | None):
        token = await self._acquire_gateway_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/x-ndjson",
        }
        payload = {
            "prompt": prompt,
            "user_id": user_id,
            "surface": SURFACE_TAG,
            "agent": AGENT_NAME,
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
                    yield _json.loads(line)

    async def _acquire_gateway_token(self) -> str:
        async with DefaultAzureCredential() as cred:
            token = await cred.get_token(GATEWAY_SCOPE)
            return token.token
