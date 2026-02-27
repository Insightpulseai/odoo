# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
TransactionCase tests for ipai_ai_widget server-side logic.

Tests cover:
  - Audit log model: metadata-only (no raw prompt/response stored)
  - Config params: bridge_url and bridge_token accessible
  - Controller ask_ai(): success path
  - Controller ask_ai(): PROMPT_REQUIRED (empty prompt)
  - Controller ask_ai(): BRIDGE_URL_NOT_CONFIGURED (empty param)
  - Controller ask_ai(): BRIDGE_TIMEOUT (requests.Timeout)
  - Controller ask_ai(): AI_KEY_NOT_CONFIGURED (bridge returns 503)
"""
import requests
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase


class TestAiAuditLog(TransactionCase):
    """Audit log model stores metadata only — no raw content fields."""

    def test_create_minimal(self):
        log = self.env["ipai.ai.audit.log"].sudo().create({
            "user_id": self.env.user.id,
            "trace_id": "test-trace-001",
            "outcome": "success",
            "latency_ms": 120,
            "prompt_len": 25,
        })
        self.assertTrue(log.id)
        self.assertEqual(log.outcome, "success")
        self.assertEqual(log.prompt_len, 25)

    def test_no_content_fields(self):
        """Security boundary: prompt, response, body must not be model fields."""
        field_names = self.env["ipai.ai.audit.log"]._fields
        self.assertNotIn("prompt", field_names)
        self.assertNotIn("response", field_names)
        self.assertNotIn("body", field_names)

    def test_all_outcomes_valid(self):
        """All selection values in _OUTCOMES can be created without error."""
        outcomes = [
            "success", "bridge_url_not_configured", "ai_key_not_configured",
            "bridge_timeout", "bridge_error", "prompt_required",
        ]
        for outcome in outcomes:
            log = self.env["ipai.ai.audit.log"].sudo().create({
                "trace_id": f"test-{outcome}",
                "outcome": outcome,
                "latency_ms": 0,
                "prompt_len": 0,
            })
            self.assertEqual(log.outcome, outcome)


class TestAiWidgetController(TransactionCase):
    """Controller ask_ai() logic (patched odoo.http.request + requests.post)."""

    def setUp(self):
        super().setUp()
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("ipai_ai_widget.bridge_url", "http://testbridge/ask")
        params.set_param("ipai_ai_widget.bridge_token", "")

    def _ask(self, prompt, record_model=None, record_id=None):
        """
        Call IpaiAiProxyController.ask_ai() with a mocked request context
        so tests do not require a live Odoo HTTP stack.
        """
        from odoo.addons.ipai_ai_widget.controllers.ai_proxy import (
            IpaiAiProxyController,
        )

        ctrl = IpaiAiProxyController()
        mock_req = MagicMock()
        mock_req.env = self.env

        with patch(
            "odoo.addons.ipai_ai_widget.controllers.ai_proxy.request", mock_req
        ):
            return ctrl.ask_ai(
                prompt=prompt,
                record_model=record_model,
                record_id=record_id,
            )

    def test_prompt_required(self):
        result = self._ask("")
        self.assertEqual(result["error"], "PROMPT_REQUIRED")
        self.assertEqual(result["status"], 400)

    def test_prompt_whitespace_only(self):
        result = self._ask("   ")
        self.assertEqual(result["error"], "PROMPT_REQUIRED")

    def test_bridge_url_not_configured(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "ipai_ai_widget.bridge_url", ""
        )
        result = self._ask("hello")
        self.assertEqual(result["error"], "BRIDGE_URL_NOT_CONFIGURED")
        self.assertEqual(result["status"], 503)

    def test_bridge_timeout(self):
        with patch("requests.post", side_effect=requests.Timeout):
            result = self._ask("hello")
        self.assertEqual(result["error"], "BRIDGE_TIMEOUT")
        self.assertEqual(result["status"], 504)

    def test_bridge_503_means_key_not_configured(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.ok = False
        with patch("requests.post", return_value=mock_resp):
            result = self._ask("hello")
        self.assertEqual(result["error"], "AI_KEY_NOT_CONFIGURED")
        self.assertEqual(result["status"], 503)

    def test_bridge_generic_error(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.ok = False
        with patch("requests.post", return_value=mock_resp):
            result = self._ask("hello")
        self.assertEqual(result["error"], "BRIDGE_ERROR")

    def test_success_returns_provider_text_model_trace(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.ok = True
        mock_resp.json.return_value = {
            "provider": "gemini",
            "text": "2 + 2 = 4",
            "model": "gemini-2.0-flash",
        }
        with patch("requests.post", return_value=mock_resp):
            result = self._ask("What is 2+2?", record_model="sale.order", record_id=1)
        self.assertNotIn("error", result)
        self.assertEqual(result["provider"], "gemini")
        self.assertEqual(result["text"], "2 + 2 = 4")
        self.assertEqual(result["model"], "gemini-2.0-flash")
        self.assertIn("trace_id", result)
        self.assertTrue(result["trace_id"])  # non-empty UUID

    def test_success_creates_audit_log(self):
        """A successful call must write an audit row with outcome=success."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.ok = True
        mock_resp.json.return_value = {"provider": "gemini", "text": "ok", "model": "m"}

        before_count = self.env["ipai.ai.audit.log"].sudo().search_count([
            ("outcome", "=", "success"),
        ])
        with patch("requests.post", return_value=mock_resp):
            result = self._ask("audit test")

        after_count = self.env["ipai.ai.audit.log"].sudo().search_count([
            ("outcome", "=", "success"),
            ("trace_id", "=", result["trace_id"]),
        ])
        self.assertEqual(after_count, 1)
