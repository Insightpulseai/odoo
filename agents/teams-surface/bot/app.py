"""
app.py — aiohttp server entrypoint for Pulser Teams bot.

Hosts the Bot Framework adapter at POST /api/messages. Forwards all
message activities to `ipai-copilot-gateway` (ACA) via authenticated
HTTP, streams responses back to Teams/Copilot Chat.

Run locally:
    python bot/app.py
Or via Microsoft 365 Agents Playground:
    npx @microsoft/teams-app-test-tool start --manifest appPackage/manifest.json
"""

from __future__ import annotations

import logging
import os
import sys
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.schema import Activity

from bot import PulserBot

LOG = logging.getLogger("pulser.app")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)


def create_app() -> web.Application:
    """Build the aiohttp app. Exposed so teamsapp.yml can import-test."""
    bot_id = os.environ.get("BOT_ID", "")
    bot_password = os.environ.get("BOT_PASSWORD", "")

    settings = BotFrameworkAdapterSettings(bot_id, bot_password)
    adapter = BotFrameworkAdapter(settings)
    bot = PulserBot()

    async def on_error(context: TurnContext, error: Exception) -> None:
        LOG.exception("bot.error %s", error)
        await context.send_activity(
            "Pulser hit an error. The team has been notified."
        )

    adapter.on_turn_error = on_error

    async def messages(req: web.Request) -> web.Response:
        if "application/json" not in req.headers.get("Content-Type", ""):
            return web.Response(status=415)

        body = await req.json()
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")

        response = await adapter.process_activity(activity, auth_header, bot.on_turn)
        if response:
            return web.json_response(data=response.body, status=response.status)
        return web.Response(status=201)

    async def health(_req: web.Request) -> web.Response:
        return web.json_response({"status": "ok", "service": "pulser-teams"})

    app = web.Application()
    app.router.add_post("/api/messages", messages)
    app.router.add_get("/healthz", health)
    return app


def main() -> None:
    app = create_app()
    port = int(os.environ.get("PORT", "3978"))
    LOG.info("pulser-teams listening on :%d", port)
    try:
        web.run_app(app, host="0.0.0.0", port=port)  # noqa: S104
    except Exception:
        LOG.exception("fatal")
        sys.exit(1)


if __name__ == "__main__":
    main()
