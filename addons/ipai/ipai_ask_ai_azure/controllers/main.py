# (c) 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
Azure OpenAI proxy controller.

Routes:
    POST /ipai/ask_ai/chat  — JSON-RPC, auth=user
        Request:  { prompt, conversation_id? }
        Response: { ok, answer, conversation_id, model, usage } on success
                  { ok: false, error, status }                  on failure

Uses Azure OpenAI Responses API shape.
"""
import json
import logging
from urllib import error as url_error
from urllib import request as url_request

from odoo import http
from odoo.http import request as odoo_request

_logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are InsightPulseAI Odoo Copilot. "
    "Answer clearly and concisely in markdown. "
    "Do not fabricate Odoo records, transactions, or business facts. "
    "If required data is unavailable, say so explicitly. "
    "Prefer operationally useful answers for ERP users."
)


def _get_config(env):
    """Read Azure OpenAI config from ir.config_parameter."""
    icp = env["ir.config_parameter"].sudo()
    return {
        "endpoint": icp.get_param("ipai_ask_ai_azure.endpoint", "").rstrip("/"),
        "api_key": icp.get_param("ipai_ask_ai_azure.api_key", ""),
        "model": icp.get_param("ipai_ask_ai_azure.model", ""),
        "api_version": icp.get_param(
            "ipai_ask_ai_azure.api_version", "preview"
        ),
    }


def _call_azure(cfg, prompt, conversation_id=None):
    """Call Azure OpenAI Responses API.

    Returns dict with ok/answer/error keys.
    """
    if not cfg["endpoint"] or not cfg["api_key"] or not cfg["model"]:
        return {
            "ok": False,
            "error": (
                "Ask AI is not configured. "
                "Set ipai_ask_ai_azure.endpoint, "
                "ipai_ask_ai_azure.api_key, and "
                "ipai_ask_ai_azure.model in System Parameters."
            ),
            "status": 500,
        }

    url = f"{cfg['endpoint']}/openai/v1/responses"

    payload = {
        "model": cfg["model"],
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            },
        ],
    }

    if conversation_id:
        payload["metadata"] = {"conversation_id": conversation_id}

    data = json.dumps(payload).encode("utf-8")
    req = url_request.Request(
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "api-key": cfg["api_key"],
        },
        method="POST",
    )

    try:
        with url_request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            parsed = json.loads(body)

        answer = ""
        for item in parsed.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in ("output_text", "text"):
                    answer += content.get("text", "")

        usage = parsed.get("usage", {})
        response_id = parsed.get("id")

        return {
            "ok": True,
            "answer": answer.strip() or "No response text returned.",
            "conversation_id": conversation_id or response_id,
            "model": cfg["model"],
            "usage": usage,
        }
    except url_error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        _logger.error("Azure OpenAI HTTP %s: %s", exc.code, detail[:500])
        return {
            "ok": False,
            "error": f"Azure OpenAI HTTP {exc.code}",
            "status": exc.code,
        }
    except Exception as exc:
        _logger.error("Azure OpenAI request failed: %s", exc)
        return {
            "ok": False,
            "error": f"Azure OpenAI request failed: {exc}",
            "status": 500,
        }


class IpaiAskAiAzureController(http.Controller):

    @http.route(
        "/ipai/ask_ai/chat",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def ipai_ask_ai_chat(self, prompt=None, conversation_id=None, **_kw):
        user = odoo_request.env.user
        if not user or user._is_public():
            return {"ok": False, "error": "Unauthorized", "status": 401}

        prompt = (prompt or "").strip()
        if not prompt:
            return {"ok": False, "error": "Prompt is required.", "status": 400}

        cfg = _get_config(odoo_request.env)
        result = _call_azure(cfg, prompt=prompt, conversation_id=conversation_id)

        _logger.info(
            "ipai_ask_ai_chat user_id=%s ok=%s conversation_id=%s model=%s",
            user.id,
            result.get("ok"),
            result.get("conversation_id"),
            result.get("model"),
        )

        # Audit log
        try:
            odoo_request.env["ipai.ask.ai.chat.log"].sudo().create({
                "user_id": user.id,
                "conversation_id": result.get("conversation_id", ""),
                "prompt_len": len(prompt),
                "outcome": "success" if result.get("ok") else "error",
                "latency_ms": 0,
                "model": cfg.get("model", ""),
            })
        except Exception:
            _logger.warning("ask_ai_azure: audit log write failed")

        return result
