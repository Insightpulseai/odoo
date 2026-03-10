# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
Shared bridge helper for IPAI AI modules.

Both ipai_ai_widget and ipai_ai_copilot use this transport layer.
Supports two backends:
  1. IPAI bridge (Gemini) — when bridge_url is configured
  2. Azure OpenAI direct — when ipai_ask_ai_azure.* params are configured

Fallback order: bridge first, Azure second. If neither is configured,
returns BRIDGE_URL_NOT_CONFIGURED.
"""
import json
import logging
from urllib import error as url_error
from urllib import request as url_request

import requests

_logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 30

AZURE_SYSTEM_PROMPT = (
    "You are InsightPulseAI Odoo Copilot. "
    "Answer clearly and concisely in markdown. "
    "Do not fabricate Odoo records, transactions, or business facts. "
    "If required data is unavailable, say so explicitly. "
    "Prefer operationally useful answers for ERP users."
)


def get_bridge_config(env):
    """Read bridge_url + bridge_token from ir.config_parameter.

    Returns:
        tuple: (bridge_url, bridge_token) — either may be empty string.
    """
    params = env["ir.config_parameter"].sudo()
    bridge_url = params.get_param("ipai_ai_widget.bridge_url", default="")
    bridge_token = params.get_param("ipai_ai_widget.bridge_token", default="")
    return bridge_url, bridge_token


def get_azure_config(env):
    """Read Azure OpenAI config from ir.config_parameter.

    Returns:
        dict: {endpoint, api_key, model, api_version} — any may be empty.
    """
    icp = env["ir.config_parameter"].sudo()
    return {
        "endpoint": icp.get_param("ipai_ask_ai_azure.endpoint", "").rstrip("/"),
        "api_key": icp.get_param("ipai_ask_ai_azure.api_key", ""),
        "model": icp.get_param("ipai_ask_ai_azure.model", ""),
        "api_version": icp.get_param(
            "ipai_ask_ai_azure.api_version", "preview"
        ),
    }


def has_azure_config(env):
    """Check if Azure OpenAI is configured (all three required params set)."""
    cfg = get_azure_config(env)
    return bool(cfg["endpoint"] and cfg["api_key"] and cfg["model"])


def call_azure_direct(prompt, env, system_prompt=None):
    """Call Azure OpenAI Responses API directly (no bridge).

    Args:
        prompt: User message string.
        env: Odoo environment (for reading config).
        system_prompt: Override system prompt (optional).

    Returns:
        tuple: (data_dict, error_code_or_none)
            On success: ({"provider": "azure", "text": ..., "model": ..., "trace_id": ...}, None)
            On failure: (None, error_code_string)
    """
    cfg = get_azure_config(env)
    if not cfg["endpoint"] or not cfg["api_key"] or not cfg["model"]:
        return None, "AZURE_NOT_CONFIGURED"

    url = f"{cfg['endpoint']}/openai/v1/responses"
    sys_prompt = system_prompt or AZURE_SYSTEM_PROMPT

    payload = {
        "model": cfg["model"],
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": sys_prompt}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            },
        ],
    }

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

        return {
            "provider": "azure",
            "text": answer.strip() or "No response returned.",
            "model": cfg["model"],
            "trace_id": parsed.get("id", ""),
        }, None

    except url_error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        _logger.error("Azure OpenAI HTTP %s: %s", exc.code, detail[:500])
        if exc.code == 401:
            return None, "AZURE_AUTH_FAILED"
        return None, "AZURE_ERROR"
    except Exception as exc:
        _logger.error("Azure OpenAI request failed: %s", exc)
        return None, "AZURE_ERROR"


def call_bridge(bridge_url, bridge_token, payload, timeout=TIMEOUT_SECONDS):
    """Shared HTTP caller for the IPAI bridge.

    Args:
        bridge_url: Full URL of the bridge endpoint.
        bridge_token: Bearer token for server-to-server auth (can be empty).
        payload: Dict to send as JSON body.
        timeout: Request timeout in seconds.

    Returns:
        tuple: (data_dict, error_code_or_none)
            On success: (response_json, None)
            On failure: (None, error_code_string)
    """
    headers = {"Content-Type": "application/json"}
    if bridge_token:
        headers["Authorization"] = f"Bearer {bridge_token}"

    try:
        resp = requests.post(
            bridge_url,
            json=payload,
            timeout=timeout,
            headers=headers,
        )
    except requests.Timeout:
        _logger.warning("IPAI bridge timeout calling %s", bridge_url)
        return None, "BRIDGE_TIMEOUT"
    except requests.RequestException as exc:
        _logger.error("IPAI bridge error — %s", exc)
        return None, "BRIDGE_ERROR"

    if resp.status_code == 503:
        _logger.warning("IPAI bridge returned 503 (AI key not configured)")
        return None, "AI_KEY_NOT_CONFIGURED"

    if not resp.ok:
        _logger.error("IPAI bridge HTTP %s", resp.status_code)
        return None, "BRIDGE_ERROR"

    try:
        data = resp.json()
    except ValueError:
        return None, "BRIDGE_ERROR"

    return data, None
