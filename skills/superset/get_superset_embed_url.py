"""
Skill: get_superset_embed_url

Build a complete Superset embedded URL with guest token for a dashboard.

Backend: token_api
"""
import os
from typing import Any, Dict

import requests


def handle(dashboard_id: str) -> Dict[str, Any]:
    """
    Returns a full Superset embedded URL and token for the given dashboard.
    Prefers the API's embedUrl field; falls back to a constructed URL.

    Args:
        dashboard_id: Superset dashboard UUID

    Returns:
        Dict with embed_url, token, iframe_src

    Raises:
        RuntimeError: If token API is not configured or returns an error
    """
    base_url = os.getenv(
        "SUPERSET_TOKEN_API_URL",
        "https://superset-embed-api.insightpulseai.net/api/superset-token",
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

    # Prefer backend-provided embedUrl
    embed_url = data.get("embedUrl")
    if not embed_url:
        superset_domain = (
            data.get("embedDomain")
            or data.get("supersetDomain")
            or os.getenv("SUPERSET_DOMAIN", "https://superset.insightpulseai.net")
        )
        superset_domain = superset_domain.rstrip("/")
        embed_url = f"{superset_domain}/embedded/{dashboard_id}"

    iframe_src = embed_url

    return {
        "embed_url": embed_url,
        "token": token,
        "iframe_src": iframe_src,
    }


# Skill metadata
SKILL_YAML = """
name: get_superset_embed_url
intent: Build a complete Superset embedded URL with guest token for a dashboard
inputs:
  dashboard_id: string
outputs:
  embed_url: string
  token: string
  iframe_src: string
error_conditions:
  - Token API returned non-2xx status
  - Token API response missing required "token" field
  - Superset domain not configured
backend: token_api
handler: "python://skills/superset/get_superset_embed_url.py"
"""
