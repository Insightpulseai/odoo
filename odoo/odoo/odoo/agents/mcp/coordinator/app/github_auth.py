"""
GitHub App Authentication Module

Handles:
- GitHub App JWT creation (RS256)
- OAuth callback for user authentication
- Installation access token minting
"""
import base64
import time
from typing import Optional, Dict, Any

import httpx
import jwt
from fastapi import APIRouter, HTTPException, Query

from .config import settings

router = APIRouter(prefix="/github", tags=["github"])


def create_app_jwt() -> str:
    """
    Create a JWT for GitHub App authentication.

    JWT is signed with RS256 using the App's private key.
    Valid for max 10 minutes per GitHub requirements.
    """
    if not settings.github_app_private_key_b64:
        raise HTTPException(
            status_code=500,
            detail="GitHub App private key not configured"
        )

    # Decode base64 private key
    private_key = base64.b64decode(settings.github_app_private_key_b64)

    now = int(time.time())
    payload = {
        "iat": now - 60,  # Issued 60s ago to handle clock drift
        "exp": now + (10 * 60),  # Expires in 10 minutes
        "iss": settings.github_app_id,
    }

    return jwt.encode(payload, private_key, algorithm="RS256")


async def get_app_installations() -> list:
    """List all installations of the GitHub App."""
    app_jwt = create_app_jwt()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/app/installations",
            headers={
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        response.raise_for_status()
        return response.json()


async def mint_installation_token(installation_id: int) -> Dict[str, Any]:
    """
    Create an installation access token for a specific installation.

    Token is valid for 1 hour and provides repository access
    scoped to the installation's permissions.
    """
    app_jwt = create_app_jwt()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        response.raise_for_status()
        return response.json()


# OAuth callback route
oauth_router = APIRouter(prefix="/oauth", tags=["oauth"])


@oauth_router.get("/github/callback")
async def github_oauth_callback(
    code: str = Query(..., description="OAuth authorization code"),
    state: Optional[str] = Query(None, description="State parameter for CSRF protection"),
):
    """
    Handle GitHub OAuth callback.

    Exchanges the authorization code for an access token.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    if not settings.github_client_id or not settings.github_client_secret:
        raise HTTPException(
            status_code=500,
            detail="GitHub OAuth not configured"
        )

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"GitHub OAuth exchange failed: {response.text}"
            )

        token_data = response.json()

        if "error" in token_data:
            raise HTTPException(
                status_code=400,
                detail=f"OAuth error: {token_data.get('error_description', token_data['error'])}"
            )

        return {
            "access_token": token_data.get("access_token"),
            "token_type": token_data.get("token_type"),
            "scope": token_data.get("scope"),
        }


# GitHub API routes (API key protected)
@router.get("/installations")
async def list_installations():
    """List all GitHub App installations."""
    try:
        installations = await get_app_installations()
        return {
            "count": len(installations),
            "installations": [
                {
                    "id": i["id"],
                    "account": i["account"]["login"],
                    "account_type": i["account"]["type"],
                    "repository_selection": i.get("repository_selection"),
                }
                for i in installations
            ]
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"GitHub API error: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/installations/{installation_id}/token")
async def create_installation_token(installation_id: int):
    """
    Mint an installation access token.

    Returns a token that can be used to authenticate as the GitHub App
    installation for repository operations.
    """
    try:
        token_data = await mint_installation_token(installation_id)
        return {
            "token": token_data.get("token"),
            "expires_at": token_data.get("expires_at"),
            "permissions": token_data.get("permissions"),
            "repository_selection": token_data.get("repository_selection"),
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"GitHub API error: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
