"""
tax-guru-surface/bot/bot.py — Tax Guru PH persona.

Mirrors the PulserBot structure from agents/teams-surface/bot/bot.py,
but overrides the surface tag, welcome message, and gateway scope.
All streaming-contract rules from docs/skills/m365-copilot-streaming-contract.md
are preserved.
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

LOG = logging.getLogger("tax_guru.bot")

AGENT_NAME = "tax-guru"
SURFACE_TAG = "teams-tax-guru"

GATEWAY_URL = os.environ.get(
    "COPILOT_GATEWAY_URL",
    "https://ipai-copilot-gateway.insightpulseai.com",
)
GATEWAY_SCOPE = os.environ.get(
    "COPILOT_GATEWAY_SCOPE",
    "api://ipai-copilot-gateway/.default",
)

WELCOME = (
    "Tax Guru PH here. Ask about BIR forms, computations, and filing deadlines.\n\n"
    "Try `/2550q`, `/2307`, `/1601c`, `/1702`, `/forms`, or `/deadlines`."
)


class TaxGuruBot(ActivityHandler):
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
            await stream.queue_informative_update("Checking the BIR reference…")

            async for chunk in self._call_gateway(
                user_text,
                user_id=turn_context.activity.from_property.aad_object_id,
            ):
                text = chunk.get("text")
                if text:
                    await stream.queue_text_chunk(text)

                attachments = chunk.get("attachments")
                if attachments:
                    stream.set_attachments(attachments)

        except Exception as err:
            LOG.exception("gateway.error %s", err)
            await stream.queue_text_chunk(
                "\n\n_Tax Guru backend error — try again in a moment._"
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
