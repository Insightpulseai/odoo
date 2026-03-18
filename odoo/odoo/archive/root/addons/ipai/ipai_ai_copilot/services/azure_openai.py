# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
Azure OpenAI service — self-contained transport for Copilot.

Supports two API modes:
  - responses  (Azure OpenAI Responses API, default)
  - chat_completions  (standard /v1/chat/completions)

Reads configuration from ir.config_parameter:
  - ipai_ask_ai_azure.base_url     → Azure endpoint (required)
  - ipai_ask_ai_azure.api_key      → API key (required)
  - ipai_ask_ai_azure.model        → Azure deployment name (required)
  - ipai_ask_ai_azure.api_mode     → "responses" | "chat_completions"
"""
import json
import logging
from urllib import error as url_error
from urllib import request as url_request

_logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 60

DEFAULT_SYSTEM_PROMPT = (
    "You are InsightPulseAI Odoo Copilot. "
    "Answer clearly and concisely in markdown. "
    "Do not fabricate Odoo records, transactions, or business facts. "
    "If required data is unavailable, say so explicitly. "
    "Prefer operationally useful answers for ERP users."
)


class AzureConfigError(Exception):
    """Raised when Azure OpenAI configuration is missing or invalid."""

    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


class AzureCallError(Exception):
    """Raised when the Azure OpenAI API call fails."""

    def __init__(self, code, message, http_status=None):
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(f"{code}: {message}")


def get_azure_config(env):
    """Read Azure OpenAI config from ir.config_parameter.

    Returns:
        dict with keys: base_url, api_key, deployment, api_mode
    """
    icp = env["ir.config_parameter"].sudo()
    return {
        "base_url": (icp.get_param("ipai_ask_ai_azure.base_url", "") or "").strip().rstrip("/"),
        "api_key": (icp.get_param("ipai_ask_ai_azure.api_key", "") or "").strip(),
        "deployment": (icp.get_param("ipai_ask_ai_azure.model", "") or "").strip(),
        "api_mode": (icp.get_param("ipai_ask_ai_azure.api_mode", "") or "responses").strip(),
    }


def has_azure_config(env):
    """Check whether Azure OpenAI is fully configured."""
    cfg = get_azure_config(env)
    return bool(cfg["base_url"] and cfg["api_key"] and cfg["deployment"])


def validate_config(cfg):
    """Raise AzureConfigError if required fields are missing."""
    if not cfg.get("base_url"):
        raise AzureConfigError("AZURE_NOT_CONFIGURED", "base_url is empty")
    if not cfg.get("api_key"):
        raise AzureConfigError("AZURE_NOT_CONFIGURED", "api_key is empty")
    if not cfg.get("deployment"):
        raise AzureConfigError(
            "AZURE_DEPLOYMENT_MISSING",
            "Azure deployment name is required. "
            "Set AZURE_OPENAI_DEPLOYMENT env var or ipai_ask_ai_azure.model config param.",
        )


def call_azure_openai(env, messages, system_prompt=None, **kwargs):
    """Call Azure OpenAI and return a structured response dict.

    Args:
        env: Odoo environment (for reading ir.config_parameter).
        messages: List of message dicts [{"role": "user", "content": "..."}]
                  or a plain string (will be wrapped as single user message).
        system_prompt: Override system prompt (optional).
        **kwargs: Additional options (timeout, etc.)

    Returns:
        dict: {
            "provider": "azure_openai",
            "text": str,
            "model": str,
            "trace_id": str,
            "api_mode": str,
        }

    Raises:
        AzureConfigError: Missing or invalid configuration.
        AzureCallError: HTTP or parsing failure.
    """
    cfg = get_azure_config(env)
    validate_config(cfg)

    # Normalize messages input
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    sys_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
    timeout = kwargs.get("timeout", TIMEOUT_SECONDS)
    api_mode = cfg["api_mode"]

    if api_mode == "chat_completions":
        return _call_chat_completions(cfg, messages, sys_prompt, timeout)
    else:
        # Default: responses API
        return _call_responses(cfg, messages, sys_prompt, timeout)


def _call_responses(cfg, messages, system_prompt, timeout):
    """Azure OpenAI Responses API (/openai/v1/responses)."""
    url = f"{cfg['base_url']}/openai/v1/responses"

    # Build input array in Responses API format
    input_messages = [
        {
            "role": "system",
            "content": [{"type": "input_text", "text": system_prompt}],
        },
    ]
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        input_messages.append({
            "role": role,
            "content": [{"type": "input_text", "text": content}],
        })

    payload = {
        "model": cfg["deployment"],
        "input": input_messages,
    }

    parsed = _http_post(url, cfg["api_key"], payload, timeout)

    # Extract text from responses output
    answer = ""
    for item in parsed.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in ("output_text", "text"):
                answer += content.get("text", "")

    return {
        "provider": "azure_openai",
        "text": answer.strip() or "No response returned.",
        "model": cfg["deployment"],
        "trace_id": parsed.get("id", ""),
        "api_mode": "responses",
    }


def _call_chat_completions(cfg, messages, system_prompt, timeout):
    """Standard OpenAI-compatible /v1/chat/completions."""
    url = f"{cfg['base_url']}/openai/v1/chat/completions"

    chat_messages = [
        {"role": "system", "content": system_prompt},
    ]
    for msg in messages:
        chat_messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", ""),
        })

    payload = {
        "model": cfg["deployment"],
        "messages": chat_messages,
    }

    parsed = _http_post(url, cfg["api_key"], payload, timeout)

    text = ""
    choices = parsed.get("choices", [])
    if choices:
        text = choices[0].get("message", {}).get("content", "")

    return {
        "provider": "azure_openai",
        "text": text.strip() or "No response returned.",
        "model": cfg["deployment"],
        "trace_id": parsed.get("id", ""),
        "api_mode": "chat_completions",
    }


def _http_post(url, api_key, payload, timeout):
    """Low-level HTTP POST using urllib (no extra deps beyond stdlib + requests)."""
    data = json.dumps(payload).encode("utf-8")
    req = url_request.Request(
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "api-key": api_key,
        },
        method="POST",
    )

    try:
        with url_request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except url_error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")[:500]
        _logger.error("Azure OpenAI HTTP %s: %s", exc.code, detail)
        if exc.code == 401:
            raise AzureCallError("AZURE_AUTH_FAILED", detail, exc.code) from exc
        if exc.code == 404:
            raise AzureCallError(
                "AZURE_DEPLOYMENT_NOT_FOUND",
                f"Deployment '{payload.get('model', '?')}' not found. "
                f"Verify AZURE_OPENAI_DEPLOYMENT matches your Azure resource.",
                exc.code,
            ) from exc
        raise AzureCallError("AZURE_ERROR", detail, exc.code) from exc
    except Exception as exc:
        _logger.error("Azure OpenAI request failed: %s", exc)
        raise AzureCallError("AZURE_ERROR", str(exc)) from exc
