"""
main.py — aiohttp entrypoint for the Pulser bot proxy.

Mounts 6 Bot Framework routes on a single ACA container app with
external ingress. Each route has its own BotFrameworkAdapter configured
with that agent's Bot ID/password (per-agent credentials from atk provision).
Handlers forward to the internal ipai-copilot-gateway via gateway.py.

Run locally:
    python -m src.main    # (requires BOT_ID_* and BOT_PASSWORD_* env)

In production (ACA):
    docker run -p 8088:8088 ipaiodoodevacr.azurecr.io/ipai-bot-proxy:latest
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.schema import Activity

from .bots import AGENT_CONFIGS, BaseAgentBot

LOG = logging.getLogger("bot_proxy.main")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

# Path at which each agent's Bot Framework webhook listens. Pulser uses
# the canonical /api/messages; others are namespaced so a single ACA app
# can host all six. Must match infra/azure/deploy-agent-routes.bicep.
ROUTES: dict[str, str] = {
    "pulser":        "/api/messages",
    "tax-guru":      "/api/tax-guru/messages",
    "doc-intel":     "/api/doc-intel/messages",
    "bank-recon":    "/api/bank-recon/messages",
    "ap-invoice":    "/api/ap-invoice/messages",
    "finance-close": "/api/finance-close/messages",
}


def _make_handler(agent_name: str, path: str) -> Any:
    """Build a per-agent aiohttp handler with its own BotFrameworkAdapter."""
    cfg = AGENT_CONFIGS[agent_name]
    env_suffix = agent_name.upper().replace("-", "_")
    bot_id = os.environ.get(f"BOT_ID_{env_suffix}", "")
    bot_password = os.environ.get(f"BOT_PASSWORD_{env_suffix}", "")

    if not bot_id:
        LOG.warning("%s: BOT_ID_%s is empty — route will reject all traffic", agent_name, env_suffix)

    adapter = BotFrameworkAdapter(BotFrameworkAdapterSettings(bot_id, bot_password))
    bot = BaseAgentBot(cfg)

    async def on_error(context: TurnContext, error: Exception) -> None:
        LOG.exception("bot.%s.error %s", agent_name, error)
        await context.send_activity(
            f"{agent_name} hit an error. The team has been notified."
        )

    adapter.on_turn_error = on_error

    async def handler(req: web.Request) -> web.Response:
        if "application/json" not in req.headers.get("Content-Type", ""):
            return web.Response(status=415, text="application/json required")

        try:
            body = await req.json()
        except Exception:
            return web.Response(status=400, text="invalid json")

        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        response = await adapter.process_activity(activity, auth_header, bot.on_turn)
        if response:
            return web.json_response(data=response.body, status=response.status)
        return web.Response(status=201)

    handler.__name__ = f"messages_{agent_name}"
    return handler


def create_app() -> web.Application:
    app = web.Application()

    for agent_name, path in ROUTES.items():
        app.router.add_post(path, _make_handler(agent_name, path))
        LOG.info("mounted %s → agent=%s", path, agent_name)

    async def health(_req: web.Request) -> web.Response:
        return web.json_response(
            {"status": "ok", "service": "bot-proxy", "routes": sorted(ROUTES.values())}
        )

    app.router.add_get("/healthz", health)
    app.router.add_get("/", health)
    return app


def main() -> None:
    app = create_app()
    port = int(os.environ.get("PORT", "8088"))
    LOG.info("bot-proxy listening on :%d (%d routes)", port, len(ROUTES))
    web.run_app(app, host="0.0.0.0", port=port)  # noqa: S104


if __name__ == "__main__":
    try:
        main()
    except Exception:
        LOG.exception("fatal")
        sys.exit(1)
