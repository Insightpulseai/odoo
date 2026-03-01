# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Plane REST API client.

Pure-Python — no Odoo dependency.  This module is the mock boundary in
Layer-2 tests:
    patch("odoo.addons.ipai_plane_connector.utils.plane_client.PlaneClient")

Keeping all requests logic here (instead of in the Odoo model) means:
- Pure-Python (Layer 1) tests can import and test this directly
- Layer-2 tests mock at a clean boundary without touching Odoo internals
"""

import hashlib
import hmac
import random
import time

import requests


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class PlaneRateLimitError(Exception):
    """Raised when the Plane API rate limit is exceeded."""

    def __init__(self, reset_at, remaining):
        self.reset_at = reset_at
        self.remaining = remaining
        super().__init__(f"Rate limited. Resets at {reset_at}")


class PlaneAPIError(Exception):
    """Raised for non-rate-limit HTTP errors from the Plane API."""

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Plane API {status_code}: {message}")


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class PlaneClient:
    """Generic Plane REST API client with rate-limiting, pagination, and auth.

    Supports two auth modes (mutually exclusive, ``oauth_token`` takes
    precedence):

    - **API key** — sent as ``X-API-Key`` header.
    - **OAuth token** — sent as ``Authorization: Bearer <token>``.

    Rate limits are tracked from response headers and the client will
    pre-emptively slow down when remaining quota is low.
    """

    DEFAULT_BASE_URL = "https://api.plane.so"
    MAX_RETRIES = 3
    MAX_PER_PAGE = 100

    def __init__(self, base_url=None, api_key=None, oauth_token=None,
                 timeout=30):
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.api_key = api_key
        self.oauth_token = oauth_token
        self.timeout = timeout
        self._rate_remaining = 60
        self._rate_reset = 0

    # -- URL helpers --------------------------------------------------------

    def _build_url(self, path):
        """Safe URL join — handles trailing slash variants."""
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    # -- Auth ---------------------------------------------------------------

    def _auth_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.oauth_token:
            headers["Authorization"] = f"Bearer {self.oauth_token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    # -- Rate limiting ------------------------------------------------------

    def _update_rate_limits(self, response):
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        if remaining is not None:
            self._rate_remaining = int(remaining)
        if reset is not None:
            self._rate_reset = int(reset)

    def _should_preemptive_backoff(self):
        return self._rate_remaining < 5

    def _backoff_delay(self, attempt):
        """Exponential backoff with jitter."""
        base = min(2 ** attempt, 8)
        return base + random.uniform(0, 1)

    # -- Core request -------------------------------------------------------

    def request(self, method, path, params=None, json_data=None,
                fields=None, expand=None):
        """Make an API request with rate-limit handling and retries.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            path: API path (e.g. ``/api/v1/workspaces``).
            params: Query-string parameters dict.
            json_data: JSON body payload dict.
            fields: Comma-separated or list of fields to return.
            expand: Comma-separated or list of relations to expand.

        Returns:
            Parsed JSON response (dict).

        Raises:
            PlaneRateLimitError: When rate limit is exhausted after retries.
            PlaneAPIError: For HTTP 4xx/5xx errors (except 429).
        """
        url = self._build_url(path)
        headers = self._auth_headers()

        if params is None:
            params = {}
        if fields:
            params["fields"] = (
                fields if isinstance(fields, str) else ",".join(fields)
            )
        if expand:
            params["expand"] = (
                expand if isinstance(expand, str) else ",".join(expand)
            )

        # Preemptive slowdown
        if self._should_preemptive_backoff():
            wait = max(0, self._rate_reset - time.time())
            if wait > 0:
                time.sleep(min(wait, 60))

        for attempt in range(self.MAX_RETRIES + 1):
            resp = requests.request(
                method, url, headers=headers, params=params,
                json=json_data, timeout=self.timeout,
            )
            self._update_rate_limits(resp)

            if resp.status_code == 429:
                if attempt < self.MAX_RETRIES:
                    delay = self._backoff_delay(attempt)
                    time.sleep(delay)
                    continue
                raise PlaneRateLimitError(
                    self._rate_reset, self._rate_remaining,
                )

            if resp.status_code >= 500 and attempt < 1:
                time.sleep(2)
                continue

            if resp.status_code >= 400:
                try:
                    msg = resp.json().get("detail", resp.text)
                except Exception:
                    msg = resp.text
                raise PlaneAPIError(resp.status_code, msg)

            return resp.json() if resp.content else {}

    # -- Convenience wrappers -----------------------------------------------

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request("PATCH", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

    # -- Pagination ---------------------------------------------------------

    def paginate(self, path, params=None, per_page=100, fields=None,
                 expand=None):
        """Generator that yields all results across pages using cursor
        pagination.

        Args:
            path: API endpoint path.
            params: Extra query-string parameters.
            per_page: Page size (capped at ``MAX_PER_PAGE``).
            fields: Fields filter forwarded to ``get()``.
            expand: Expand filter forwarded to ``get()``.

        Yields:
            Individual result dicts from each page.
        """
        per_page = min(per_page, self.MAX_PER_PAGE)
        if params is None:
            params = {}
        params["per_page"] = per_page
        cursor = None

        while True:
            if cursor:
                params["cursor"] = cursor
            data = self.get(
                path, params=params, fields=fields, expand=expand,
            )
            results = data.get("results", [])
            yield from results

            if not data.get("next_page_results", False):
                break
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                break
            cursor = next_cursor
