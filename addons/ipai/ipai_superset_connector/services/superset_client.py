# -*- coding: utf-8 -*-
"""
Superset API Client with token caching.

Implements the guest token flow:
1. /api/v1/security/login → access token
2. /api/v1/security/csrf_token → CSRF token
3. /api/v1/security/guest_token/ → guest token (Bearer + X-CSRFToken)

Token caching reduces API calls to Superset (access + CSRF cached for ~4 min).
"""
import logging
import time
import requests
from threading import Lock

_logger = logging.getLogger(__name__)

# Module-level token cache (thread-safe)
_token_cache = {}
_cache_lock = Lock()
TOKEN_TTL_SECONDS = 240  # 4 minutes cache TTL


class SupersetClientError(Exception):
    """Raised when Superset API calls fail."""
    pass


class SupersetClient:
    """
    Superset REST API client for guest token issuance.

    Usage:
        client = SupersetClient(base_url, username, password)
        token = client.get_guest_token(dashboard_id, user_info, rls_rules)
    """

    def __init__(self, base_url: str, username: str, password: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self._cache_key = f"{self.base_url}:{self.username}"

    def _get_cached_tokens(self):
        """Retrieve cached access + CSRF tokens if still valid."""
        with _cache_lock:
            cached = _token_cache.get(self._cache_key)
            if cached and cached.get("expires_at", 0) > time.time():
                return cached.get("access_token"), cached.get("csrf_token")
            return None, None

    def _set_cached_tokens(self, access_token: str, csrf_token: str):
        """Cache tokens with TTL."""
        with _cache_lock:
            _token_cache[self._cache_key] = {
                "access_token": access_token,
                "csrf_token": csrf_token,
                "expires_at": time.time() + TOKEN_TTL_SECONDS,
            }

    def _clear_cache(self):
        """Clear cached tokens (on auth failure)."""
        with _cache_lock:
            _token_cache.pop(self._cache_key, None)

    def login_access_token(self) -> str:
        """
        Authenticate with Superset and get access token.

        POST /api/v1/security/login
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/security/login",
                json={
                    "username": self.username,
                    "password": self.password,
                    "provider": "db",
                    "refresh": True,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")
            if not access_token:
                raise SupersetClientError("No access_token in login response")
            return access_token
        except requests.RequestException as e:
            _logger.error("Superset login failed: %s", e)
            raise SupersetClientError(f"Superset login failed: {e}") from e

    def get_csrf_token(self, access_token: str) -> str:
        """
        Get CSRF token for protected endpoints.

        GET /api/v1/security/csrf_token/
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/security/csrf_token/",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            csrf_token = data.get("result")
            if not csrf_token:
                raise SupersetClientError("No CSRF token in response")
            return csrf_token
        except requests.RequestException as e:
            _logger.error("Superset CSRF token fetch failed: %s", e)
            raise SupersetClientError(f"CSRF token fetch failed: {e}") from e

    def get_guest_token(
        self,
        dashboard_id: str,
        user_info: dict,
        rls_rules: list = None,
    ) -> str:
        """
        Get guest token for embedding a dashboard.

        POST /api/v1/security/guest_token/

        Args:
            dashboard_id: Superset dashboard ID (string)
            user_info: Dict with username, first_name, last_name
            rls_rules: Optional list of RLS rule dicts [{"clause": "..."}]

        Returns:
            Guest token string for Superset Embedded SDK
        """
        # Try cached tokens first
        access_token, csrf_token = self._get_cached_tokens()

        if not access_token or not csrf_token:
            # Fetch fresh tokens
            access_token = self.login_access_token()
            csrf_token = self.get_csrf_token(access_token)
            self._set_cached_tokens(access_token, csrf_token)

        payload = {
            "user": user_info,
            "resources": [{"type": "dashboard", "id": str(dashboard_id)}],
            "rls": rls_rules or [],
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/security/guest_token/",
                json=payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-CSRFToken": csrf_token,
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )

            # Handle auth errors by clearing cache and retrying once
            if response.status_code in (401, 403):
                _logger.warning("Superset auth failed, clearing cache and retrying")
                self._clear_cache()
                access_token = self.login_access_token()
                csrf_token = self.get_csrf_token(access_token)
                self._set_cached_tokens(access_token, csrf_token)

                response = requests.post(
                    f"{self.base_url}/api/v1/security/guest_token/",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "X-CSRFToken": csrf_token,
                        "Content-Type": "application/json",
                    },
                    timeout=self.timeout,
                )

            response.raise_for_status()
            data = response.json()
            token = data.get("token")
            if not token:
                raise SupersetClientError("No token in guest_token response")
            return token

        except requests.RequestException as e:
            _logger.error("Superset guest token request failed: %s", e)
            raise SupersetClientError(f"Guest token request failed: {e}") from e

    def health_check(self) -> dict:
        """
        Check Superset API health.

        GET /api/v1/version

        Returns:
            Version info dict or raises SupersetClientError
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/version",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _logger.error("Superset health check failed: %s", e)
            raise SupersetClientError(f"Health check failed: {e}") from e


def get_superset_client_from_params(env) -> SupersetClient:
    """
    Factory function to create SupersetClient from Odoo system parameters.

    Args:
        env: Odoo environment

    Returns:
        Configured SupersetClient instance
    """
    ICP = env["ir.config_parameter"].sudo()
    base_url = ICP.get_param("ipai_superset.base_url", "")
    username = ICP.get_param("ipai_superset.username", "")
    password = ICP.get_param("ipai_superset.password", "")

    if not all([base_url, username, password]):
        raise SupersetClientError(
            "Missing Superset configuration. Set ipai_superset.base_url, "
            "ipai_superset.username, and ipai_superset.password in System Parameters."
        )

    return SupersetClient(base_url, username, password)
