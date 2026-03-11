# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
Provider bridge — unified entry point for Copilot LLM calls.

Resolution order:
  1. ipai.ai.provider (if model exists and has an active default with azure_openai type)
  2. Direct Azure OpenAI call (if ir.config_parameter keys are set)
  3. ipai.ai.provider with any other type (fallback)

Returns a unified response dict or error tuple matching the controller's expectations.
"""
import logging
import os
import time

import requests

from .azure_openai import (
    AzureCallError,
    AzureConfigError,
    call_azure_openai,
    has_azure_config,
)

_logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = (
    "You are InsightPulseAI Odoo Copilot. "
    "Answer clearly and concisely in markdown. "
    "Do not fabricate Odoo records, transactions, or business facts. "
    "If required data is unavailable, say so explicitly. "
    "Prefer operationally useful answers for ERP users."
)


def call_provider(env, messages, system_prompt=None, **kwargs):
    """Call the best available LLM provider.

    Args:
        env: Odoo environment.
        messages: str or list of message dicts.
        system_prompt: Override system prompt (optional).
        **kwargs: Forwarded to underlying provider call.

    Returns:
        tuple: (data_dict, error_code_or_none)
            On success: ({"provider": ..., "text": ..., "model": ..., "trace_id": ...}, None)
            On failure: (None, error_code_string)
    """
    sys_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    # ── Path 1: Azure OpenAI direct (preferred for ACA deployments) ──────
    if has_azure_config(env):
        try:
            result = call_azure_openai(env, messages, system_prompt=sys_prompt, **kwargs)
            return result, None
        except AzureConfigError as exc:
            _logger.warning("Azure config error: %s", exc.code)
            return None, exc.code
        except AzureCallError as exc:
            _logger.error("Azure call error: %s", exc.code)
            return None, exc.code

    # ── Path 2: ipai.ai.provider model ───────────────────────────────────
    provider = _get_default_provider(env)
    if provider:
        return _call_provider_model(provider, messages, env, sys_prompt)

    # ── No provider configured ───────────────────────────────────────────
    return None, "NO_PROVIDER_CONFIGURED"


def _get_default_provider(env):
    """Return the default active ipai.ai.provider record, or None."""
    try:
        Provider = env["ipai.ai.provider"].sudo()
        return Provider.search(
            [("is_default", "=", True), ("active", "=", True)],
            limit=1,
        ) or None
    except Exception:
        # Model might not exist if ipai_ai_core not installed
        return None


def _call_provider_model(provider, messages, env, system_prompt):
    """Call LLM via ipai.ai.provider record configuration.

    Supports: openai, anthropic, google, ollama, azure_openai, supabase_edge.
    """
    # Resolve API key
    api_key = ""
    if provider.api_key_param:
        api_key = (
            env["ir.config_parameter"]
            .sudo()
            .get_param(provider.api_key_param, default="")
        )
        if not api_key:
            api_key = os.environ.get(provider.api_key_param, "")

    if not api_key:
        _logger.warning(
            "Provider %s: no API key (param: %s)", provider.name, provider.api_key_param
        )
        return None, "PROVIDER_KEY_NOT_CONFIGURED"

    base_url = (provider.base_url or "").rstrip("/")
    model = provider.model_name or ""
    if not base_url or not model:
        return None, "PROVIDER_NOT_CONFIGURED"

    # Normalize messages to plain prompt string for provider calls
    if isinstance(messages, list):
        prompt = "\n".join(
            m.get("content", "") for m in messages if m.get("role") == "user"
        )
    else:
        prompt = str(messages)

    # Route by provider type
    if provider.provider_type == "azure_openai":
        # Use our dedicated Azure service
        try:
            result = call_azure_openai(env, messages, system_prompt=system_prompt)
            return result, None
        except (AzureConfigError, AzureCallError) as exc:
            return None, exc.code

    elif provider.provider_type in ("openai", "ollama"):
        return _call_openai_compat(base_url, api_key, model, prompt, system_prompt, provider)

    elif provider.provider_type == "anthropic":
        return _call_anthropic(base_url, api_key, model, prompt, system_prompt, provider)

    elif provider.provider_type == "google":
        return _call_google(base_url, api_key, model, prompt, system_prompt, provider)

    else:
        # Fallback: try OpenAI-compatible
        return _call_openai_compat(base_url, api_key, model, prompt, system_prompt, provider)


def _call_openai_compat(base_url, api_key, model, prompt, system_prompt, provider):
    """OpenAI-compatible /v1/chat/completions."""
    url = f"{base_url}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": provider.max_tokens or 4096,
        "temperature": provider.temperature if provider.temperature else 0.7,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    t0 = time.monotonic()
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
    except requests.Timeout:
        return None, "PROVIDER_TIMEOUT"
    except requests.RequestException as exc:
        _logger.error("Provider %s error: %s", provider.name, exc)
        return None, "PROVIDER_ERROR"

    latency_ms = (time.monotonic() - t0) * 1000

    if not resp.ok:
        _logger.error("Provider %s HTTP %s: %s", provider.name, resp.status_code, resp.text[:500])
        if resp.status_code == 401:
            return None, "PROVIDER_AUTH_FAILED"
        return None, "PROVIDER_ERROR"

    try:
        data = resp.json()
    except ValueError:
        return None, "PROVIDER_ERROR"

    text = ""
    choices = data.get("choices", [])
    if choices:
        text = choices[0].get("message", {}).get("content", "")

    tokens_used = data.get("usage", {}).get("total_tokens", 0)
    try:
        provider.sudo().update_stats(latency_ms, tokens_used)
    except Exception:
        pass

    return {
        "provider": provider.name,
        "text": text.strip() or "No response returned.",
        "model": model,
        "trace_id": data.get("id", ""),
    }, None


def _call_anthropic(base_url, api_key, model, prompt, system_prompt, provider):
    """Anthropic Messages API."""
    url = f"{base_url}/v1/messages"
    payload = {
        "model": model,
        "max_tokens": provider.max_tokens or 4096,
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    t0 = time.monotonic()
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
    except requests.Timeout:
        return None, "PROVIDER_TIMEOUT"
    except requests.RequestException as exc:
        _logger.error("Provider %s error: %s", provider.name, exc)
        return None, "PROVIDER_ERROR"

    latency_ms = (time.monotonic() - t0) * 1000

    if not resp.ok:
        _logger.error("Provider %s HTTP %s: %s", provider.name, resp.status_code, resp.text[:500])
        return None, "PROVIDER_ERROR"

    try:
        data = resp.json()
    except ValueError:
        return None, "PROVIDER_ERROR"

    text = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            text += block.get("text", "")

    usage = data.get("usage", {})
    tokens_used = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
    try:
        provider.sudo().update_stats(latency_ms, tokens_used)
    except Exception:
        pass

    return {
        "provider": provider.name,
        "text": text.strip() or "No response returned.",
        "model": model,
        "trace_id": data.get("id", ""),
    }, None


def _call_google(base_url, api_key, model, prompt, system_prompt, provider):
    """Google Gemini generateContent API."""
    url = f"{base_url}/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": provider.max_tokens or 4096,
            "temperature": provider.temperature if provider.temperature else 0.7,
        },
    }

    t0 = time.monotonic()
    try:
        resp = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}, timeout=60
        )
    except requests.Timeout:
        return None, "PROVIDER_TIMEOUT"
    except requests.RequestException as exc:
        _logger.error("Provider %s error: %s", provider.name, exc)
        return None, "PROVIDER_ERROR"

    latency_ms = (time.monotonic() - t0) * 1000

    if not resp.ok:
        _logger.error("Provider %s HTTP %s: %s", provider.name, resp.status_code, resp.text[:500])
        return None, "PROVIDER_ERROR"

    try:
        data = resp.json()
    except ValueError:
        return None, "PROVIDER_ERROR"

    text = ""
    candidates = data.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            text += part.get("text", "")

    tokens_used = data.get("usageMetadata", {}).get("totalTokenCount", 0)
    try:
        provider.sudo().update_stats(latency_ms, tokens_used)
    except Exception:
        pass

    return {
        "provider": provider.name,
        "text": text.strip() or "No response returned.",
        "model": model,
        "trace_id": "",
    }, None
