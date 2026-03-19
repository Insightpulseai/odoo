"""
Odoo TransactionCase tests for ipai_mail_bridge_zoho.models.mail_mail.

Runs via Odoo's test runner (not plain pytest):
    python odoo-bin --test-enable --test-tags ipai_mail_bridge_zoho -d odoo_dev

Test coverage targets
---------------------
B1  bridge enabled, HTTP 200           → mail.state = "sent"
B2  email_to empty                     → state = "exception" (UserError, no HTTP call)
B3  HTTP 500 response                  → state = "exception", failure_reason set
B4  requests.post raises RequestException → state = "exception"
B5  bridge disabled (no env vars)      → super().send() path, bridge HTTP not called
B6  HTTP 500 + raise_exception=True    → exception propagates to caller
"""

import os
from unittest.mock import MagicMock, patch

import requests as _requests_lib  # for RequestException/ConnectionError references

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Patch the `requests` module *as imported* in mail_mail.py (the call site)
_PATCH_REQUESTS = "odoo.addons.ipai_mail_bridge_zoho.models.mail_mail.requests"

# Env vars that enable the bridge
_BRIDGE_ENV = {
    "ZOHO_MAIL_BRIDGE_URL": "https://fake-bridge.test",
    "ZOHO_MAIL_BRIDGE_SECRET": "fake-secret-32-chars-xxxxxxxxxxxxx",
}


def _mock_response(status_code=200, json_data=None, text=""):
    """Return a MagicMock that quacks like a requests.Response."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.text = text
    mock_resp.json.return_value = json_data if json_data is not None else {"ok": True}
    return mock_resp


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


@tagged("ipai_mail_bridge_zoho", "-at_install", "post_install")
class TestMailBridgeZohoSend(TransactionCase):
    """Layer-2 regression tests for ipai_mail_bridge_zoho.send() business logic."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.mail = self.env["mail.mail"].create(
            {
                "subject": "Bridge Test Subject",
                "body": "Hello from the bridge test suite.",
                "email_from": "test@insightpulseai.com",
                "email_to": "dest@example.com",
            }
        )

    # ------------------------------------------------------------------
    # B1 — bridge enabled, HTTP 200 → mail.state = "sent"
    # ------------------------------------------------------------------

    def test_b1_bridge_success_sets_state_sent(self):
        """Bridge enabled, HTTP 200 + ok=True → mail.state becomes 'sent'."""
        mock_resp = _mock_response(status_code=200, json_data={"ok": True})
        with patch.dict(os.environ, _BRIDGE_ENV):
            with patch(_PATCH_REQUESTS + ".post", return_value=mock_resp):
                self.mail.send()

        self.assertEqual(self.mail.state, "sent")
        self.assertFalse(self.mail.failure_reason)

    # ------------------------------------------------------------------
    # B2 — email_to empty → UserError before HTTP call, state = "exception"
    # ------------------------------------------------------------------

    def test_b2_empty_email_to_no_http_call(self):
        """email_to='' → UserError inside send(), requests.post NOT called."""
        self.mail.write({"email_to": ""})
        mock_post = MagicMock()

        with patch.dict(os.environ, _BRIDGE_ENV):
            with patch(_PATCH_REQUESTS + ".post", mock_post):
                self.mail.send()  # send() catches the UserError; does not re-raise

        mock_post.assert_not_called()
        self.assertEqual(self.mail.state, "exception")
        self.assertIn("No recipients", self.mail.failure_reason)

    # ------------------------------------------------------------------
    # B3 — HTTP 500 response → state = "exception", failure_reason set
    # ------------------------------------------------------------------

    def test_b3_http_500_sets_state_exception(self):
        """HTTP 500 → UserError raised in _ipai_bridge_send_one; state='exception'."""
        mock_resp = _mock_response(status_code=500, text="Internal Server Error")

        with patch.dict(os.environ, _BRIDGE_ENV):
            with patch(_PATCH_REQUESTS + ".post", return_value=mock_resp):
                self.mail.send()

        self.assertEqual(self.mail.state, "exception")
        self.assertIn("500", self.mail.failure_reason)

    # ------------------------------------------------------------------
    # B4 — RequestException → state = "exception"
    # ------------------------------------------------------------------

    def test_b4_request_exception_sets_state_exception(self):
        """requests.post raises ConnectionError → state='exception'."""
        with patch.dict(os.environ, _BRIDGE_ENV):
            with patch(
                _PATCH_REQUESTS + ".post",
                side_effect=_requests_lib.exceptions.ConnectionError("connection refused"),
            ):
                self.mail.send()

        self.assertEqual(self.mail.state, "exception")
        self.assertIn("connection refused", self.mail.failure_reason)

    # ------------------------------------------------------------------
    # B5 — bridge disabled (no env vars) → super().send() used, HTTP not called
    # ------------------------------------------------------------------

    def test_b5_bridge_disabled_skips_bridge_http(self):
        """No env vars → _ipai_bridge_enabled() False; bridge requests.post not called."""
        mock_post = MagicMock()

        # Empty strings make _bridge_url() and _bridge_secret() return falsy values
        disabled_env = {"ZOHO_MAIL_BRIDGE_URL": "", "ZOHO_MAIL_BRIDGE_SECRET": ""}
        with patch.dict(os.environ, disabled_env):
            # Verify the guard condition directly
            self.assertFalse(self.mail._ipai_bridge_enabled())

            with patch(_PATCH_REQUESTS + ".post", mock_post):
                try:
                    # super().send() will be called; it may raise in the test env
                    # (no SMTP configured) — that is acceptable for this test
                    self.mail.send()
                except Exception:
                    pass

        # The bridge HTTP call must never have been made
        mock_post.assert_not_called()

    # ------------------------------------------------------------------
    # B6 — HTTP 500 + raise_exception=True → exception propagates
    # ------------------------------------------------------------------

    def test_b6_http_500_raise_exception_propagates(self):
        """HTTP 500 + raise_exception=True → exception propagates to caller."""
        mock_resp = _mock_response(status_code=500, text="Gateway Error")

        with patch.dict(os.environ, _BRIDGE_ENV):
            with patch(_PATCH_REQUESTS + ".post", return_value=mock_resp):
                with self.assertRaises(Exception):
                    self.mail.send(raise_exception=True)

        # write({"state": "exception"}) happens before the re-raise
        self.assertEqual(self.mail.state, "exception")
