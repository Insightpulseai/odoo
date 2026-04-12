"""
bots.py — Per-agent persona definitions + shared ActivityHandler.

All six agents share the same forwarding logic; they differ only in
surface tag, welcome message, gateway endpoint, and whether they accept
file uploads.

NOTE: The MS Learn streaming-contract doc describes an API
(`StreamingResponse.queue_text_chunk`, `end_stream`, `set_attachments`)
that only ships in the .NET/TypeScript Agents SDKs — the Python
botbuilder-core SDK does not expose those primitives. This implementation
buffers the NDJSON chunks from the gateway and sends ONE final activity
per turn plus an initial "typing" indicator. Token-by-token streaming in
Python requires the newer `teams-ai` SDK (follow-up work).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import Activity, ActivityTypes, Attachment, ChannelAccount

from .gateway import stream_gateway

LOG = logging.getLogger("bot_proxy.bots")


@dataclass(frozen=True)
class AgentConfig:
    name: str              # internal key — matches agents/<name>-surface/
    surface_tag: str       # passed to gateway as `surface` field
    welcome: str           # on_members_added message
    gateway_path: str = "/chat"        # "/extract" for doc-intel
    accepts_files: bool = False
    timeout_seconds: int = 60


class BaseAgentBot(ActivityHandler):
    """Thin ActivityHandler — persona driven by AgentConfig."""

    def __init__(self, cfg: AgentConfig) -> None:
        self.cfg = cfg

    async def on_members_added_activity(
        self,
        members_added: list[ChannelAccount],
        turn_context: TurnContext,
    ) -> None:
        for member in members_added:
            if member.id == turn_context.activity.recipient.id:
                continue
            await turn_context.send_activity(self.cfg.welcome)

    async def on_message_activity(self, turn_context: TurnContext) -> None:
        user_text = (turn_context.activity.text or "").strip()
        file_refs: list[dict[str, Any]] = []
        if self.cfg.accepts_files:
            for att in turn_context.activity.attachments or []:
                if not att.content_type:
                    continue
                content_url = getattr(att, "content_url", None) or (
                    att.content.get("downloadUrl")
                    if isinstance(att.content, dict)
                    else None
                )
                file_refs.append(
                    {
                        "name": att.name,
                        "content_type": att.content_type,
                        "content_url": content_url,
                    }
                )

        if not user_text and not file_refs:
            return

        # Acknowledge the user turn with a typing indicator so Teams
        # doesn't sit silent while the gateway does work.
        await turn_context.send_activity(
            Activity(type=ActivityTypes.typing)
        )

        payload: dict[str, Any] = {
            "prompt": user_text,
            "user_id": turn_context.activity.from_property.aad_object_id,
            "surface": self.cfg.surface_tag,
            "agent": self.cfg.name,
            "stream": True,
        }
        if file_refs:
            payload["files"] = file_refs

        buffered_text: list[str] = []
        buffered_attachments: list[Attachment] = []
        try:
            async for chunk in stream_gateway(self.cfg.gateway_path, payload):
                text = chunk.get("text")
                if text:
                    buffered_text.append(text)
                for raw in chunk.get("attachments") or []:
                    # NDJSON attachment fields are already Activity-shaped
                    buffered_attachments.append(Attachment().deserialize(raw))

        except Exception as err:
            LOG.exception("%s.gateway.error %s", self.cfg.name, err)
            await turn_context.send_activity(
                f"_{self.cfg.name} backend error — try again in a moment._"
            )
            return

        # One final activity with the accumulated response.
        body = "".join(buffered_text).strip()
        if not body and not buffered_attachments:
            await turn_context.send_activity(
                f"_{self.cfg.name} returned no content._"
            )
            return

        reply = Activity(
            type=ActivityTypes.message,
            text=body or None,
            attachments=buffered_attachments or None,
        )
        await turn_context.send_activity(reply)


# ─── Agent configurations — ONE per IPAI custom engine agent ────────────────
AGENT_CONFIGS: dict[str, AgentConfig] = {
    "pulser": AgentConfig(
        name="pulser",
        surface_tag="teams-pulser",
        welcome=(
            "Hi — I'm Pulser. Ask me about Odoo, BIR, or Azure.\n\n"
            "Try `/odoo`, `/bir`, `/infra`, or `/doctrine`."
        ),
    ),
    "tax-guru": AgentConfig(
        name="tax-guru",
        surface_tag="teams-tax-guru",
        welcome=(
            "Tax Guru PH here. Ask about BIR forms, computations, and filing deadlines.\n\n"
            "Try `/2550q`, `/2307`, `/1601c`, `/1702`, `/forms`, or `/deadlines`."
        ),
    ),
    "doc-intel": AgentConfig(
        name="doc-intel",
        surface_tag="teams-doc-intel",
        welcome=(
            "Doc Intelligence ready. Upload a PDF or image, or tell me what to extract.\n\n"
            "Try `/invoice`, `/receipt`, `/id`, `/2307`, or `/extract <schema>`."
        ),
        gateway_path="/extract",
        accepts_files=True,
        timeout_seconds=120,
    ),
    "bank-recon": AgentConfig(
        name="bank-recon",
        surface_tag="teams-bank-recon",
        welcome=(
            "Bank Recon ready. Upload a bank statement (OFX, CSV, PDF) or ask about "
            "unreconciled entries.\n\n"
            "Try `/unreconciled`, `/match`, `/summary`, or `/banks`."
        ),
        accepts_files=True,
        timeout_seconds=120,
    ),
    "ap-invoice": AgentConfig(
        name="ap-invoice",
        surface_tag="teams-ap-invoice",
        welcome=(
            "AP Invoice ready. Upload a vendor invoice PDF and I'll create a draft bill.\n\n"
            "Try `/process`, `/pending`, `/approve <id>`, `/reject <id>`, `/vendor`."
        ),
        accepts_files=True,
        timeout_seconds=120,
    ),
    "finance-close": AgentConfig(
        name="finance-close",
        surface_tag="teams-finance-close",
        welcome=(
            "Finance Close ready. I orchestrate your monthly close — checklist, status, "
            "variance review, and period lock.\n\n"
            "Try `/status`, `/checklist`, `/close`, `/variance`, or `/reopen`."
        ),
    ),
}
