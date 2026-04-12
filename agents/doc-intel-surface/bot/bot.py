"""
doc-intel-surface/bot/bot.py — Document Intelligence persona.

Extracts structured data from file attachments. `supportsFiles: true` in
the manifest means incoming messages may carry attachments — forwarded
to ipai-copilot-gateway which runs the Foundry DI pipeline (13 tools).
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

LOG = logging.getLogger("doc_intel.bot")

AGENT_NAME = "doc-intel"
SURFACE_TAG = "teams-doc-intel"

GATEWAY_URL = os.environ.get(
    "COPILOT_GATEWAY_URL",
    "https://ipai-copilot-gateway.insightpulseai.com",
)
GATEWAY_SCOPE = os.environ.get(
    "COPILOT_GATEWAY_SCOPE",
    "api://ipai-copilot-gateway/.default",
)

WELCOME = (
    "Doc Intelligence ready. Upload a PDF or image, or tell me what to extract.\n\n"
    "Try `/invoice`, `/receipt`, `/id`, `/2307`, or `/extract <schema>`."
)


class DocIntelBot(ActivityHandler):
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
        # Extract any file attachments — Teams delivers them with contentUrl
        attachments = turn_context.activity.attachments or []
        file_refs = [
            {
                "name": att.name,
                "content_type": att.content_type,
                "content_url": getattr(att, "content_url", None) or (
                    att.content.get("downloadUrl") if isinstance(att.content, dict) else None
                ),
            }
            for att in attachments
            if att.content_type and att.content_type.startswith(("application/", "image/"))
        ]

        if not user_text and not file_refs:
            return

        stream = StreamingResponse(turn_context)
        try:
            await stream.queue_informative_update(
                "Extracting…" if file_refs else "Thinking…"
            )

            async for chunk in self._call_gateway(
                prompt=user_text,
                file_refs=file_refs,
                user_id=turn_context.activity.from_property.aad_object_id,
            ):
                text = chunk.get("text")
                if text:
                    await stream.queue_text_chunk(text)

                chunk_attachments = chunk.get("attachments")
                if chunk_attachments:
                    stream.set_attachments(chunk_attachments)

        except Exception as err:
            LOG.exception("gateway.error %s", err)
            await stream.queue_text_chunk(
                "\n\n_Doc Intelligence backend error — try again in a moment._"
            )
        finally:
            await stream.end_stream()

    async def _call_gateway(
        self,
        prompt: str,
        file_refs: list[dict],
        user_id: str | None,
    ):
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
            "files": file_refs,
            "stream": True,
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(
                f"{GATEWAY_URL}/extract", json=payload, timeout=120
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
