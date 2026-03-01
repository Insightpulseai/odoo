# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""
Unit tests for PlaneClient (pure-Python layer).

Mock boundary:
    patch("odoo.addons.ipai_plane_connector.utils.plane_client.requests")

Test coverage targets
---------------------
C1  API key auth header          → X-API-Key present
C2  OAuth token auth header      → Authorization: Bearer present
C3  OAuth takes precedence       → Both set, Bearer wins
C4  Base URL construction        → Trailing slashes normalised
C5  Rate limit tracking          → Headers update internal state
C6  429 retry + backoff          → Retries on rate limit, raises after max
C7  Pagination                   → Multiple pages yielded, stops on last
C8  4xx error mapping            → PlaneAPIError with status + message
C9  5xx retry once               → 500 retried once, then raises
C10 Empty response body          → Returns empty dict
C11 Fields/expand params         → Passed as query-string parameters
"""

from unittest.mock import MagicMock, patch

from odoo.tests import TransactionCase, tagged

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PATCH_REQUESTS = (
    "odoo.addons.ipai_plane_connector.utils.plane_client.requests"
)


def _mock_response(status_code=200, json_data=None, headers=None,
                   content=b"ok", text="ok"):
    """Build a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.content = content
    resp.text = text
    resp.json.return_value = json_data if json_data is not None else {}
    return resp


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


@tagged("ipai_plane_connector", "-at_install", "post_install")
class TestPlaneClient(TransactionCase):
    """Layer-1-style tests for PlaneClient, run inside Odoo test harness."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def _make_client(self, **kwargs):
        from odoo.addons.ipai_plane_connector.utils.plane_client import (
            PlaneClient,
        )
        return PlaneClient(**kwargs)

    # ------------------------------------------------------------------
    # C1 — API key auth header
    # ------------------------------------------------------------------

    def test_c1_api_key_header(self):
        """API key auth sends X-API-Key header."""
        client = self._make_client(api_key="test-key-123")
        headers = client._auth_headers()
        self.assertEqual(headers.get("X-API-Key"), "test-key-123")
        self.assertNotIn("Authorization", headers)

    # ------------------------------------------------------------------
    # C2 — OAuth token auth header
    # ------------------------------------------------------------------

    def test_c2_oauth_header(self):
        """OAuth token auth sends Authorization: Bearer header."""
        client = self._make_client(oauth_token="oauth-tok-abc")
        headers = client._auth_headers()
        self.assertEqual(headers["Authorization"], "Bearer oauth-tok-abc")
        self.assertNotIn("X-API-Key", headers)

    # ------------------------------------------------------------------
    # C3 — OAuth takes precedence over API key
    # ------------------------------------------------------------------

    def test_c3_oauth_precedence(self):
        """When both api_key and oauth_token are set, Bearer wins."""
        client = self._make_client(
            api_key="key-123", oauth_token="tok-abc",
        )
        headers = client._auth_headers()
        self.assertEqual(headers["Authorization"], "Bearer tok-abc")
        self.assertNotIn("X-API-Key", headers)

    # ------------------------------------------------------------------
    # C4 — Base URL construction
    # ------------------------------------------------------------------

    def test_c4_base_url_trailing_slash(self):
        """Trailing slash on base_url is normalised."""
        client = self._make_client(
            base_url="https://plane.example.com/",
        )
        url = client._build_url("/api/v1/workspaces")
        self.assertEqual(url, "https://plane.example.com/api/v1/workspaces")

    def test_c4_path_without_leading_slash(self):
        """Path without leading slash gets one added."""
        client = self._make_client(
            base_url="https://plane.example.com",
        )
        url = client._build_url("api/v1/issues")
        self.assertEqual(url, "https://plane.example.com/api/v1/issues")

    # ------------------------------------------------------------------
    # C5 — Rate limit tracking
    # ------------------------------------------------------------------

    def test_c5_rate_limit_tracking(self):
        """Rate limit headers update internal state."""
        client = self._make_client(api_key="k")
        resp = _mock_response(headers={
            "X-RateLimit-Remaining": "10",
            "X-RateLimit-Reset": "1700000000",
        })
        client._update_rate_limits(resp)
        self.assertEqual(client._rate_remaining, 10)
        self.assertEqual(client._rate_reset, 1700000000)

    # ------------------------------------------------------------------
    # C6 — 429 retry and backoff
    # ------------------------------------------------------------------

    @patch(_PATCH_REQUESTS)
    def test_c6_429_retries_then_raises(self, mock_requests):
        """429 is retried up to MAX_RETRIES, then PlaneRateLimitError."""
        from odoo.addons.ipai_plane_connector.utils.plane_client import (
            PlaneRateLimitError,
        )
        mock_requests.request.return_value = _mock_response(
            status_code=429, headers={},
        )
        client = self._make_client(api_key="k")
        # Patch sleep to avoid actual delays
        with patch(
            "odoo.addons.ipai_plane_connector.utils.plane_client.time.sleep"
        ):
            with self.assertRaises(PlaneRateLimitError):
                client.get("/api/v1/test")
        # Should have been called MAX_RETRIES + 1 times
        self.assertEqual(
            mock_requests.request.call_count, client.MAX_RETRIES + 1,
        )

    # ------------------------------------------------------------------
    # C7 — Pagination
    # ------------------------------------------------------------------

    @patch(_PATCH_REQUESTS)
    def test_c7_pagination_multiple_pages(self, mock_requests):
        """Paginate yields results across multiple pages."""
        page1 = _mock_response(json_data={
            "results": [{"id": "1"}, {"id": "2"}],
            "next_page_results": True,
            "next_cursor": "cursor_abc",
        })
        page2 = _mock_response(json_data={
            "results": [{"id": "3"}],
            "next_page_results": False,
        })
        mock_requests.request.side_effect = [page1, page2]

        client = self._make_client(api_key="k")
        results = list(client.paginate("/api/v1/items", per_page=2))

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["id"], "1")
        self.assertEqual(results[2]["id"], "3")

    @patch(_PATCH_REQUESTS)
    def test_c7_pagination_single_page(self, mock_requests):
        """Paginate stops when next_page_results is False."""
        page1 = _mock_response(json_data={
            "results": [{"id": "only"}],
            "next_page_results": False,
        })
        mock_requests.request.return_value = page1

        client = self._make_client(api_key="k")
        results = list(client.paginate("/api/v1/items"))

        self.assertEqual(len(results), 1)
        self.assertEqual(mock_requests.request.call_count, 1)

    # ------------------------------------------------------------------
    # C8 — 4xx error mapping
    # ------------------------------------------------------------------

    @patch(_PATCH_REQUESTS)
    def test_c8_4xx_raises_plane_api_error(self, mock_requests):
        """HTTP 404 raises PlaneAPIError with status and message."""
        from odoo.addons.ipai_plane_connector.utils.plane_client import (
            PlaneAPIError,
        )
        mock_requests.request.return_value = _mock_response(
            status_code=404,
            json_data={"detail": "Not found"},
            text="Not found",
        )
        client = self._make_client(api_key="k")
        with self.assertRaises(PlaneAPIError) as ctx:
            client.get("/api/v1/missing")
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("Not found", ctx.exception.message)

    # ------------------------------------------------------------------
    # C9 — 5xx retry once
    # ------------------------------------------------------------------

    @patch(_PATCH_REQUESTS)
    def test_c9_500_retried_once(self, mock_requests):
        """500 is retried once, then raises PlaneAPIError if still failing."""
        from odoo.addons.ipai_plane_connector.utils.plane_client import (
            PlaneAPIError,
        )
        error_resp = _mock_response(
            status_code=500, json_data={"detail": "Internal"},
            text="Internal",
        )
        mock_requests.request.return_value = error_resp

        client = self._make_client(api_key="k")
        with patch(
            "odoo.addons.ipai_plane_connector.utils.plane_client.time.sleep"
        ):
            with self.assertRaises(PlaneAPIError) as ctx:
                client.get("/api/v1/broken")
        self.assertEqual(ctx.exception.status_code, 500)
        # First attempt + one retry = 2 calls
        self.assertEqual(mock_requests.request.call_count, 2)

    @patch(_PATCH_REQUESTS)
    def test_c9_500_succeeds_on_retry(self, mock_requests):
        """500 on first attempt, 200 on retry returns data."""
        error_resp = _mock_response(status_code=500, text="Error")
        success_resp = _mock_response(
            status_code=200, json_data={"ok": True},
        )
        mock_requests.request.side_effect = [error_resp, success_resp]

        client = self._make_client(api_key="k")
        with patch(
            "odoo.addons.ipai_plane_connector.utils.plane_client.time.sleep"
        ):
            result = client.get("/api/v1/flaky")
        self.assertEqual(result, {"ok": True})

    # ------------------------------------------------------------------
    # C10 — Empty response body
    # ------------------------------------------------------------------

    @patch(_PATCH_REQUESTS)
    def test_c10_empty_body_returns_empty_dict(self, mock_requests):
        """Empty response body returns empty dict."""
        mock_requests.request.return_value = _mock_response(
            status_code=200, content=b"",
        )
        client = self._make_client(api_key="k")
        result = client.get("/api/v1/empty")
        self.assertEqual(result, {})

    # ------------------------------------------------------------------
    # C11 — Fields and expand params
    # ------------------------------------------------------------------

    @patch(_PATCH_REQUESTS)
    def test_c11_fields_and_expand_params(self, mock_requests):
        """Fields and expand are passed as query-string parameters."""
        mock_requests.request.return_value = _mock_response(
            json_data={"id": "1"},
        )
        client = self._make_client(api_key="k")
        client.get(
            "/api/v1/issues",
            fields=["name", "state"],
            expand=["assignees"],
        )
        call_kwargs = mock_requests.request.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get(
            "params", {},
        )
        self.assertEqual(params.get("fields"), "name,state")
        self.assertEqual(params.get("expand"), "assignees")
