"""
Skill: validate_superset_health

Check the health of Superset and the Guest Token API.

Backend: http
"""
import os
from typing import Any, Dict

import requests


def _check_health(url: str) -> Dict[str, Any]:
    """Check health of a single endpoint."""
    try:
        resp = requests.get(url, timeout=5)
    except requests.RequestException as exc:
        return {"ok": False, "error": str(exc), "status_code": None, "body": None}

    try:
        body = resp.json()
    except ValueError:
        body = resp.text

    return {
        "ok": resp.ok,
        "error": None if resp.ok else f"HTTP {resp.status_code}",
        "status_code": resp.status_code,
        "body": body,
    }


def handle(check_token_api: bool, check_superset: bool) -> Dict[str, Any]:
    """
    Validate health of Superset and the Guest Token API.

    Args:
        check_token_api: Whether to check the token API health
        check_superset: Whether to check Superset health

    Returns:
        Dict with status, superset_ok, token_api_ok, details

    Raises:
        None (always returns a result dict)
    """
    token_api_ok = True
    superset_ok = True
    details: Dict[str, Any] = {}

    if check_token_api:
        token_api_url = os.getenv(
            "SUPERSET_TOKEN_API_HEALTH_URL",
            "https://superset-embed-api.insightpulseai.com/health",
        )
        token_result = _check_health(token_api_url)
        details["token_api"] = token_result
        token_api_ok = bool(token_result.get("ok"))

    if check_superset:
        superset_base = os.getenv(
            "SUPERSET_DOMAIN", "https://superset.insightpulseai.com"
        ).rstrip("/")
        superset_health_url = os.getenv(
            "SUPERSET_HEALTH_URL", f"{superset_base}/health"
        )
        superset_result = _check_health(superset_health_url)
        details["superset"] = superset_result
        superset_ok = bool(superset_result.get("ok"))

    if (check_token_api and not token_api_ok) and (check_superset and not superset_ok):
        status = "error"
    elif token_api_ok and superset_ok:
        status = "ok"
    else:
        status = "degraded"

    return {
        "status": status,
        "superset_ok": superset_ok,
        "token_api_ok": token_api_ok,
        "details": details,
    }


# Skill metadata
SKILL_YAML = """
name: validate_superset_health
intent: Check the health of Superset and the Guest Token API
inputs:
  check_token_api: boolean
  check_superset: boolean
outputs:
  status: string
  superset_ok: boolean
  token_api_ok: boolean
  details: object
error_conditions:
  - Both Superset and Token API endpoints unreachable
  - Health endpoints returned non-2xx responses
backend: http
handler: "python://skills/superset/validate_superset_health.py"
"""
