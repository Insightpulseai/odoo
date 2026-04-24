# -*- coding: utf-8 -*-
"""
test_controller.py — HttpCase tests for the PulserChatController endpoints.

Tests exercise:
- /ipai/pulser_chat/bootstrap  (auth=user, POST)
- /ipai/pulser_chat/message    (auth=user, POST)

Upstream Pulser calls are monkey-patched so no external network is needed.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from odoo.tests.common import HttpCase
from odoo.tests import tagged


@tagged("ipai", "ipai_pulser_chat", "-at_install", "post_install")
class TestBootstrapEndpoint(HttpCase):
    """Tests for /ipai/pulser_chat/bootstrap."""

    def _post_json(self, path, payload=None):
        """POST a JSON-RPC-style body and return the parsed response dict."""
        body = json.dumps({"jsonrpc": "2.0", "method": "call", "id": 1, "params": payload or {}})
        resp = self.url_open(
            path,
            data=body.encode(),
            headers={"Content-Type": "application/json"},
        )
        return resp.json().get("result", {})

    def test_bootstrap_returns_enabled_false_by_default(self):
        """Bootstrap returns enabled=False when feature is off (default seed)."""
        self.authenticate("admin", "admin")
        result = self._post_json("/ipai/pulser_chat/bootstrap")
        self.assertIn("enabled", result)
        self.assertFalse(result["enabled"])

    def test_bootstrap_backend_configured_false_when_url_empty(self):
        """backend_configured is False when backend URL is not set."""
        self.authenticate("admin", "admin")
        # Ensure URL is empty
        self.env["ir.config_parameter"].sudo().set_param(
            "ipai.pulser_chat.backend_url", ""
        )
        result = self._post_json("/ipai/pulser_chat/bootstrap")
        self.assertFalse(result.get("backend_configured"))

    def test_bootstrap_returns_company_name(self):
        """Bootstrap includes the current company name."""
        self.authenticate("admin", "admin")
        result = self._post_json("/ipai/pulser_chat/bootstrap")
        self.assertIn("company_name", result)
        self.assertTrue(result["company_name"])

    def test_bootstrap_requires_auth(self):
        """Unauthenticated requests must be rejected (redirect to /web/login)."""
        resp = self.url_open(
            "/ipai/pulser_chat/bootstrap",
            data=json.dumps({"jsonrpc": "2.0", "method": "call", "id": 1, "params": {}}).encode(),
            headers={"Content-Type": "application/json"},
        )
        # Odoo redirects unauthenticated JSON requests to login; the RPC layer
        # may return an error or a redirect — neither should be a 200 OK with
        # a valid result.
        result = resp.json()
        # Either "error" key present, or "result" is None/empty.
        has_error = "error" in result
        result_empty = not result.get("result")
        self.assertTrue(
            has_error or result_empty,
            "Unauthenticated bootstrap should not return a valid result",
        )


@tagged("ipai", "ipai_pulser_chat", "-at_install", "post_install")
class TestMessageEndpoint(HttpCase):
    """Tests for /ipai/pulser_chat/message."""

    def setUp(self):
        super().setUp()
        self.authenticate("admin", "admin")
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("ipai.pulser_chat.enabled", "True")
        ICP.set_param("ipai.pulser_chat.backend_url", "https://pulser.example.com/chat")
        ICP.set_param("ipai.pulser_chat.timeout_seconds", "30")

    def _post_message(self, payload):
        body = json.dumps({"jsonrpc": "2.0", "method": "call", "id": 1, "params": payload})
        resp = self.url_open(
            "/ipai/pulser_chat/message",
            data=body.encode(),
            headers={"Content-Type": "application/json"},
        )
        return resp.json().get("result", {})

    def _mock_proxy(self, return_value):
        """Context manager that patches _proxy_message to return *return_value*."""
        return patch(
            "odoo.addons.ipai_pulser_chat.controllers.pulser_chat"
            ".PulserChatController._proxy_message",
            return_value=return_value,
        )

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    def test_valid_message_returns_ok(self):
        """A valid message with a mocked upstream returns ok=True and content."""
        upstream_response = {
            "content": "Hello from Pulser!",
            "conversation_id": "conv-abc-123",
        }
        with self._mock_proxy(upstream_response):
            result = self._post_message({"message": "Hello", "context": {}, "conversation_id": None})
        self.assertTrue(result.get("ok"))
        self.assertEqual(result.get("content"), "Hello from Pulser!")
        self.assertEqual(result.get("conversation_id"), "conv-abc-123")

    def test_conversation_id_preserved(self):
        """conversation_id from upstream is returned to the client."""
        upstream_response = {
            "message": "Continued reply",
            "conversation_id": "conv-xyz-999",
        }
        with self._mock_proxy(upstream_response):
            result = self._post_message(
                {"message": "Follow-up", "context": {}, "conversation_id": "conv-xyz-999"}
            )
        self.assertEqual(result.get("conversation_id"), "conv-xyz-999")

    # ------------------------------------------------------------------
    # Validation failures (no upstream call needed)
    # ------------------------------------------------------------------

    def test_empty_message_rejected(self):
        """Empty message string returns ok=False."""
        result = self._post_message({"message": "", "context": {}, "conversation_id": None})
        self.assertFalse(result.get("ok"))
        self.assertIn("empty", result.get("error", "").lower())

    def test_whitespace_only_message_rejected(self):
        """Whitespace-only message is treated as empty."""
        result = self._post_message({"message": "   ", "context": {}, "conversation_id": None})
        self.assertFalse(result.get("ok"))

    def test_oversized_message_rejected(self):
        """Messages exceeding 8 000 characters return ok=False."""
        result = self._post_message(
            {"message": "x" * 8001, "context": {}, "conversation_id": None}
        )
        self.assertFalse(result.get("ok"))
        self.assertIn("8", result.get("error", ""))  # '8 000' appears in error

    def test_disabled_returns_error(self):
        """Message endpoint returns ok=False when feature is disabled."""
        self.env["ir.config_parameter"].sudo().set_param(
            "ipai.pulser_chat.enabled", "False"
        )
        result = self._post_message({"message": "Hello", "context": {}, "conversation_id": None})
        self.assertFalse(result.get("ok"))
        self.assertIn("disabled", result.get("error", "").lower())

    def test_missing_url_returns_error(self):
        """Message endpoint returns ok=False when backend URL is empty."""
        self.env["ir.config_parameter"].sudo().set_param(
            "ipai.pulser_chat.backend_url", ""
        )
        result = self._post_message({"message": "Hello", "context": {}, "conversation_id": None})
        self.assertFalse(result.get("ok"))

    # ------------------------------------------------------------------
    # Upstream failure modes
    # ------------------------------------------------------------------

    def test_upstream_timeout_returns_ok_false(self):
        """TimeoutError from upstream produces a clean ok=False response."""
        with patch(
            "odoo.addons.ipai_pulser_chat.controllers.pulser_chat"
            ".PulserChatController._proxy_message",
            side_effect=TimeoutError("timed out"),
        ):
            result = self._post_message(
                {"message": "Hello", "context": {}, "conversation_id": None}
            )
        self.assertFalse(result.get("ok"))
        self.assertIn("time", result.get("error", "").lower())

    def test_upstream_http_error_returns_ok_false(self):
        """HTTPError from upstream produces a clean ok=False response."""
        import urllib.error
        http_err = urllib.error.HTTPError(
            url="https://pulser.example.com/chat",
            code=503,
            msg="Service Unavailable",
            hdrs={},
            fp=None,
        )
        with patch(
            "odoo.addons.ipai_pulser_chat.controllers.pulser_chat"
            ".PulserChatController._proxy_message",
            side_effect=http_err,
        ):
            result = self._post_message(
                {"message": "Hello", "context": {}, "conversation_id": None}
            )
        self.assertFalse(result.get("ok"))
        self.assertIn("503", result.get("error", ""))

    def test_upstream_url_error_returns_ok_false(self):
        """URLError (network failure) produces a clean ok=False response."""
        import urllib.error
        url_err = urllib.error.URLError("connection refused")
        with patch(
            "odoo.addons.ipai_pulser_chat.controllers.pulser_chat"
            ".PulserChatController._proxy_message",
            side_effect=url_err,
        ):
            result = self._post_message(
                {"message": "Hello", "context": {}, "conversation_id": None}
            )
        self.assertFalse(result.get("ok"))
        self.assertIn("unreachable", result.get("error", "").lower())

    def test_upstream_invalid_json_returns_ok_false(self):
        """JSONDecodeError from upstream produces a clean ok=False response."""
        with patch(
            "odoo.addons.ipai_pulser_chat.controllers.pulser_chat"
            ".PulserChatController._proxy_message",
            side_effect=json.JSONDecodeError("invalid", "", 0),
        ):
            result = self._post_message(
                {"message": "Hello", "context": {}, "conversation_id": None}
            )
        self.assertFalse(result.get("ok"))

    def test_upstream_oversized_response_returns_ok_false(self):
        """ValueError from body size cap produces a clean ok=False response."""
        with patch(
            "odoo.addons.ipai_pulser_chat.controllers.pulser_chat"
            ".PulserChatController._proxy_message",
            side_effect=ValueError("response exceeded limit"),
        ):
            result = self._post_message(
                {"message": "Hello", "context": {}, "conversation_id": None}
            )
        self.assertFalse(result.get("ok"))

    # ------------------------------------------------------------------
    # Context sanitisation
    # ------------------------------------------------------------------

    def test_invalid_context_model_ignored(self):
        """context_model containing injection chars is sanitised to False."""
        upstream_response = {"content": "OK", "conversation_id": None}
        with self._mock_proxy(upstream_response):
            result = self._post_message(
                {
                    "message": "Hello",
                    "context": {"context_model": "res.model; DROP TABLE", "surface": "erp"},
                    "conversation_id": None,
                }
            )
        # Should succeed — the bad model name is stripped, not rejected
        self.assertTrue(result.get("ok"))

    def test_valid_context_model_passes(self):
        """Valid dot-notation context_model is forwarded to upstream."""
        upstream_response = {"content": "OK", "conversation_id": None}
        with self._mock_proxy(upstream_response) as mock_proxy:
            self._post_message(
                {
                    "message": "Hello",
                    "context": {"context_model": "sale.order", "context_res_id": 42},
                    "conversation_id": None,
                }
            )
        # Verify the proxy was called with the sanitised context
        call_args = mock_proxy.call_args
        payload = call_args[0][1]  # second positional arg is payload
        odoo_ctx = payload["session"]["odoo_context"]
        self.assertEqual(odoo_ctx["context_model"], "sale.order")
        self.assertEqual(odoo_ctx["context_res_id"], 42)
