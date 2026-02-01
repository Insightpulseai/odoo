"""
Skill: get_superset_guest_token

Generate a Superset guest JWT for a specific dashboard.

Backend: token_api
"""
import os
import time
from typing import Any, Dict

import requests


def handle(dashboard_id: str) -> Dict[str, Any]:
    """
    Calls the Superset Guest Token API and returns a normalized token payload.

    Args:
        dashboard_id: Superset dashboard UUID

    Returns:
        Dict with token, audience, embed_domain, expires_at

    Raises:
        RuntimeError: If token API is not configured or returns an error
    """
    base_url = os.getenv(
        "SUPERSET_TOKEN_API_URL",
        "https://superset-embed-api.insightpulseai.com/api/superset-token",
    )
    if not base_url:
        raise RuntimeError("SUPERSET_TOKEN_API_URL is not configured")

    params = {"dashboard_id": dashboard_id}
    try:
        response = requests.get(base_url, params=params, timeout=10)
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to call token API: {exc}") from exc

    if not response.ok:
        raise RuntimeError(
            f"Token API error: HTTP {response.status_code} - {response.text}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("Token API did not return valid JSON") from exc

    token = data.get("token")
    if not token:
        raise RuntimeError('Token API response missing required field "token"')

    # Normalize audience and embed domain
    audience = data.get("audience") or os.getenv(
        "SUPERSET_GUEST_TOKEN_AUDIENCE", "superset"
    )
    embed_domain = (
        data.get("embedDomain")
        or data.get("supersetDomain")
        or os.getenv("SUPERSET_DOMAIN", "https://superset.insightpulseai.com")
    )

    # Normalize expiry
    expires_at = None
    if isinstance(data.get("expiresAt"), (int, float)):
        expires_at = int(data["expiresAt"])
    elif isinstance(data.get("exp"), (int, float)):
        expires_at = int(data["exp"])
    else:
        expires_at = int(time.time()) + 3600

    return {
        "token": token,
        "audience": audience,
        "embed_domain": embed_domain,
        "expires_at": expires_at,
    }


# Skill metadata
SKILL_YAML = """
name: get_superset_guest_token
intent: Generate a Superset guest JWT for a specific dashboard
inputs:
  dashboard_id: string
outputs:
  token: string
  audience: string
  embed_domain: string
  expires_at: integer
error_conditions:
  - Token API returned non-2xx status
  - Token API response missing required "token" field
  - Token API URL not configured
backend: token_api
handler: "python://skills/superset/get_superset_guest_token.py"
"""
