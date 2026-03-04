# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
Shared bridge helper for IPAI AI modules.

Both ipai_ai_widget and ipai_ai_copilot use this transport layer
to call the IPAI provider bridge (server-to-server).
"""
import logging

import requests

_logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 30


def get_bridge_config(env):
    """Read bridge_url + bridge_token from ir.config_parameter.

    Returns:
        tuple: (bridge_url, bridge_token) — either may be empty string.
    """
    params = env["ir.config_parameter"].sudo()
    bridge_url = params.get_param("ipai_ai_widget.bridge_url", default="")
    bridge_token = params.get_param("ipai_ai_widget.bridge_token", default="")
    return bridge_url, bridge_token


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
