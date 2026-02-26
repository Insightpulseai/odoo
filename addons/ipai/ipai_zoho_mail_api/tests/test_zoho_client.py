# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Unit tests for ZohoMailClient.

Uses unittest.mock to avoid real HTTP calls and Odoo DB dependency.
Run standalone:  python -m pytest addons/ipai/ipai_zoho_mail_api/tests/test_zoho_client.py
Run via Odoo:    ./odoo-bin -d odoo_dev --test-enable -i ipai_zoho_mail_api
"""

import time
import unittest
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase


# ── Minimal env mock (for standalone runs without Odoo DB) ───────────────────

def _make_env(params: dict):
    """Return a fake Odoo env whose ir.config_parameter behaves like a dict."""
    cfg = MagicMock()
    cfg.sudo.return_value = cfg
    cfg.get_param.side_effect = lambda k, default="": params.get(k, default)
    cfg.set_param.side_effect = lambda k, v: params.update({k: v})
    env = MagicMock()
    env.__getitem__.side_effect = lambda _: cfg
    return env, params


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestTokenRefresh(unittest.TestCase):
    """Token refresh logic and caching."""

    def _client(self, params):
        from odoo.addons.ipai_zoho_mail_api.services.zoho_client import ZohoMailClient
        env, store = _make_env(params)
        return ZohoMailClient(env), store

    @patch("requests.post")
    def test_refresh_called_when_cache_empty(self, mock_post):
        """Fresh start → token endpoint is called."""
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "access_token": "tok-abc",
                "expires_in": 3600,
            },
        )
        client, store = self._client(
            {
                "ipai.zoho.client_id": "CLIENT_ID",
                "ipai.zoho.client_secret": "SECRET",
                "ipai.zoho.refresh_token": "REFRESH",
            }
        )
        token = client.get_access_token()
        self.assertEqual(token, "tok-abc")
        mock_post.assert_called_once()
        # Token cached in store
        self.assertEqual(store.get("ipai.zoho.access_token"), "tok-abc")

    @patch("requests.post")
    def test_cached_token_not_refreshed(self, mock_post):
        """Valid cached token is returned without hitting the endpoint."""
        future = str(time.time() + 7200)
        client, _ = self._client(
            {
                "ipai.zoho.client_id": "CLIENT_ID",
                "ipai.zoho.client_secret": "SECRET",
                "ipai.zoho.refresh_token": "REFRESH",
                "ipai.zoho.access_token": "cached-token",
                "ipai.zoho.access_token_expires_at": future,
            }
        )
        token = client.get_access_token()
        self.assertEqual(token, "cached-token")
        mock_post.assert_not_called()

    @patch("requests.post")
    def test_expired_token_refreshed(self, mock_post):
        """Expired cached token triggers a refresh."""
        past = str(time.time() - 10)
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {"access_token": "new-token", "expires_in": 3600},
        )
        client, _ = self._client(
            {
                "ipai.zoho.client_id": "CLIENT_ID",
                "ipai.zoho.client_secret": "SECRET",
                "ipai.zoho.refresh_token": "REFRESH",
                "ipai.zoho.access_token": "old-token",
                "ipai.zoho.access_token_expires_at": past,
            }
        )
        token = client.get_access_token()
        self.assertEqual(token, "new-token")
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_missing_credentials_raise(self, mock_post):
        """Missing credentials raise ValueError before hitting the API."""
        client, _ = self._client({})
        with self.assertRaises(ValueError, msg="should raise on missing creds"):
            client.get_access_token()
        mock_post.assert_not_called()


class TestSendMessage(unittest.TestCase):
    """Payload mapping for send_message()."""

    def _client(self, params):
        from odoo.addons.ipai_zoho_mail_api.services.zoho_client import ZohoMailClient
        env, store = _make_env(params)
        return ZohoMailClient(env), store

    def _base_params(self):
        future = str(time.time() + 7200)
        return {
            "ipai.zoho.client_id": "C",
            "ipai.zoho.client_secret": "S",
            "ipai.zoho.refresh_token": "R",
            "ipai.zoho.account_id": "2190180000000008002",
            "ipai.zoho.access_token": "valid-token",
            "ipai.zoho.access_token_expires_at": future,
        }

    @patch("requests.post")
    def test_send_html_body(self, mock_post):
        """HTML body is mapped to content + mailFormat=html."""
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "status": {"code": 200, "description": "success"},
                "data": {"messageId": "1234", "subject": "Hello"},
            },
        )
        client, _ = self._client(self._base_params())
        client.send_message(
            from_addr="no-reply@insightpulseai.com",
            to_addrs=["jake.tolentino@insightpulseai.com"],
            subject="Hello",
            html_body="<p>Hello</p>",
        )
        sent = mock_post.call_args
        body = sent.kwargs.get("json") or sent[1].get("json")
        self.assertEqual(body["mailFormat"], "html")
        self.assertEqual(body["content"], "<p>Hello</p>")
        self.assertEqual(body["fromAddress"], "no-reply@insightpulseai.com")

    @patch("requests.post")
    def test_send_plain_body(self, mock_post):
        """Plain text body maps to mailFormat=plaintext."""
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {"status": {"code": 200}, "data": {"messageId": "5678"}},
        )
        client, _ = self._client(self._base_params())
        client.send_message(
            from_addr="no-reply@insightpulseai.com",
            to_addrs=["test@example.com"],
            subject="Plain test",
            text_body="Hello plain",
        )
        body = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1]["json"]
        self.assertEqual(body["mailFormat"], "plaintext")

    @patch("requests.post")
    def test_cc_and_bcc_included(self, mock_post):
        """CC and BCC addresses appear in payload."""
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {"status": {"code": 200}, "data": {"messageId": "999"}},
        )
        client, _ = self._client(self._base_params())
        client.send_message(
            from_addr="no-reply@insightpulseai.com",
            to_addrs=["a@example.com"],
            subject="CC test",
            html_body="<p>hi</p>",
            cc_addrs=["cc@example.com"],
            bcc_addrs=["bcc@example.com"],
        )
        body = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1]["json"]
        self.assertIn("ccAddress", body)
        self.assertIn("bccAddress", body)

    @patch("requests.post")
    def test_non_200_raises_runtime_error(self, mock_post):
        """Non-2xx from Zoho raises RuntimeError."""
        mock_post.return_value = MagicMock(ok=False, status_code=401, text="Unauthorized")
        client, _ = self._client(self._base_params())
        with self.assertRaises(RuntimeError):
            client.send_message(
                from_addr="no-reply@insightpulseai.com",
                to_addrs=["test@example.com"],
                subject="Fail",
                html_body="<p>x</p>",
            )

    def test_missing_account_id_raises(self):
        """Missing account_id raises ValueError without calling the API."""
        params = self._base_params()
        params.pop("ipai.zoho.account_id")
        client, _ = self._client(params)
        with self.assertRaises(ValueError):
            client.send_message(
                from_addr="no-reply@insightpulseai.com",
                to_addrs=["test@example.com"],
                subject="No account",
                html_body="<p>x</p>",
            )


# ── Odoo TransactionCase (runs in odoo-bin --test-enable context) ─────────────


class TestZohoClientOdoo(TransactionCase):
    """Integration tests using real ir.config_parameter."""

    @patch("requests.post")
    def test_token_round_trip_in_odoo(self, mock_post):
        """Token refresh + cache using real ir.config_parameter."""
        from odoo.addons.ipai_zoho_mail_api.services.zoho_client import ZohoMailClient

        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {"access_token": "live-tok", "expires_in": 3600},
        )

        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("ipai.zoho.client_id", "C")
        ICP.set_param("ipai.zoho.client_secret", "S")
        ICP.set_param("ipai.zoho.refresh_token", "R")
        # Clear any cached token
        ICP.set_param("ipai.zoho.access_token", "")
        ICP.set_param("ipai.zoho.access_token_expires_at", "0")

        client = ZohoMailClient(self.env)
        token = client.get_access_token()
        self.assertEqual(token, "live-tok")

        # Second call should hit cache, not the endpoint again
        token2 = client.get_access_token()
        self.assertEqual(token2, "live-tok")
        self.assertEqual(mock_post.call_count, 1)
