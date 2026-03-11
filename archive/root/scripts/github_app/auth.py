#!/usr/bin/env python3
"""
GitHub App Authentication Helper — pulser-hub
==============================================
Mint JWT tokens and obtain installation tokens for the pulser-hub GitHub App.

Usage:
    # As CLI (prints installation token to stdout)
    python3 scripts/github_app/auth.py

    # As library
    from scripts.github_app.auth import get_installation_token
    token = get_installation_token()

Environment variables:
    GITHUB_APP_ID          — App ID (2191216)
    GITHUB_CLIENT_ID       — Client ID (Iv23liwGL7fnYySPPAjS), used as JWT iss
    GITHUB_APP_PRIVATE_KEY — RSA private key (PEM format, multiline)
    GITHUB_INSTALLATION_ID — Installation ID (optional, auto-discovered if omitted)

SSOT: ssot/github/apps/pulser-hub.yaml
Companion: supabase/functions/github-app-auth/index.ts (TypeScript Edge Function)
"""

import json
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# ---------------------------------------------------------------------------
# Configuration — SSOT values as defaults, env vars override
# ---------------------------------------------------------------------------
APP_ID = os.environ.get("GITHUB_APP_ID", "2191216")
CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "Iv23liwGL7fnYySPPAjS")
PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY", "")
INSTALLATION_ID = os.environ.get("GITHUB_INSTALLATION_ID", "")
ORG = "Insightpulseai"

# JWT issuer: prefer client_id (GitHub recommended), fall back to app_id
JWT_ISSUER = CLIENT_ID or APP_ID


def _ensure_private_key() -> str:
    """Return PEM private key from env or raise."""
    key = PRIVATE_KEY
    if not key:
        # Try reading from file path
        key_path = os.environ.get("GITHUB_APP_PRIVATE_KEY_PATH", "")
        if key_path and Path(key_path).exists():
            key = Path(key_path).read_text()
    if not key:
        raise RuntimeError(
            "GITHUB_APP_PRIVATE_KEY or GITHUB_APP_PRIVATE_KEY_PATH required. "
            "See ssot/secrets/registry.yaml for storage locations."
        )
    return key


def mint_jwt() -> str:
    """
    Mint a GitHub App JWT for authentication.

    Uses PyJWT if available, otherwise falls back to manual JWT construction.
    The JWT is valid for 10 minutes (GitHub maximum).
    """
    key = _ensure_private_key()
    now = int(time.time())
    payload = {
        "iat": now - 60,       # 60s in the past for clock-drift tolerance
        "exp": now + 600,      # 10-minute max (GitHub limit)
        "iss": JWT_ISSUER,     # client_id preferred; app_id as fallback
    }

    try:
        import jwt  # PyJWT
        return jwt.encode(payload, key, algorithm="RS256")
    except ImportError:
        pass

    # Fallback: manual JWT construction (no external deps)
    import base64
    import hashlib
    import struct

    def _b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    header = _b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    body = _b64url(json.dumps(payload).encode())
    signing_input = f"{header}.{body}".encode()

    # Parse PEM and sign with RSA
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        private_key = serialization.load_pem_private_key(key.encode(), password=None)
        signature = private_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
        return f"{header}.{body}.{_b64url(signature)}"
    except ImportError:
        raise RuntimeError(
            "Either PyJWT or cryptography package required for JWT signing. "
            "Install: pip install PyJWT cryptography"
        )


def _github_api(path: str, token: str, method: str = "GET", body: bytes = None) -> dict:
    """Make an authenticated GitHub API request."""
    url = f"https://api.github.com{path}"
    req = Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"GitHub API {method} {path} → {e.code}: {error_body}")


def discover_installation_id(app_jwt: str) -> str:
    """
    Find the installation ID for the org.
    Uses GET /app/installations and filters for ORG.
    """
    installations = _github_api("/app/installations", app_jwt)
    for inst in installations:
        account = inst.get("account", {})
        if account.get("login", "").lower() == ORG.lower():
            return str(inst["id"])
    raise RuntimeError(
        f"No installation found for org '{ORG}'. "
        "Install the pulser-hub app on the org first."
    )


def get_installation_token(installation_id: str = None) -> dict:
    """
    Get an installation access token for the pulser-hub GitHub App.

    Returns:
        dict with keys: token, expires_at, permissions, repository_selection
    """
    app_jwt = mint_jwt()

    if not installation_id:
        installation_id = INSTALLATION_ID or discover_installation_id(app_jwt)

    result = _github_api(
        f"/app/installations/{installation_id}/access_tokens",
        app_jwt,
        method="POST",
        body=b"{}",
    )
    return {
        "token": result["token"],
        "expires_at": result["expires_at"],
        "permissions": result.get("permissions", {}),
        "repository_selection": result.get("repository_selection", ""),
        "installation_id": installation_id,
    }


def get_app_info(app_jwt: str = None) -> dict:
    """Get authenticated App info (permissions, events, etc.)."""
    if not app_jwt:
        app_jwt = mint_jwt()
    return _github_api("/app", app_jwt)


def main():
    """CLI entry point: prints installation token JSON to stdout."""
    try:
        token_data = get_installation_token()
        print(json.dumps(token_data, indent=2))
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
