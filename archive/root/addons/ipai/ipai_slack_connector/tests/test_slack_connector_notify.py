"""
Odoo TransactionCase tests for ipai_slack_connector.models.slack_notify.

Runs via Odoo's test runner (not plain pytest):
    python odoo-bin --test-enable --test-tags ipai_slack_connector -d odoo_dev

Test coverage targets
---------------------
S1  env set, post_webhook succeeds     → _ipai_post_message returns True
S2  SLACK_WEBHOOK_URL not set          → UserError before post_webhook called
S3  post_webhook raises HTTPError      → UserError propagates to caller
S4  channel kwarg forwarded            → payload contains text + channel
S5  _ipai_slack_enabled() when no env  → returns False
"""

import os
from unittest.mock import MagicMock, patch

import requests as _requests_lib  # for HTTPError reference

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Mock boundary: patch post_webhook at the call site (the module attribute)
_PATCH_WEBHOOK = "odoo.addons.ipai_slack_connector.utils.slack_client.post_webhook"

# Env vars that enable the Slack connector
_SLACK_ENV = {
    "SLACK_WEBHOOK_URL": "https://hooks.slack.example/services/T0000/B0000/FAKETOKEN"
}


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


@tagged("ipai_slack_connector", "-at_install", "post_install")
class TestSlackConnectorNotify(TransactionCase):
    """Layer-2 regression tests for ipai.slack.connector._ipai_post_message."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.connector = self.env["ipai.slack.connector"]

    # ------------------------------------------------------------------
    # S1 — env set, post_webhook succeeds → returns True
    # ------------------------------------------------------------------

    def test_s1_success_returns_true(self):
        """Env set, post_webhook mock returns → _ipai_post_message returns True."""
        mock_webhook = MagicMock(return_value=MagicMock(status_code=200))

        with patch.dict(os.environ, _SLACK_ENV):
            with patch(_PATCH_WEBHOOK, mock_webhook):
                result = self.connector._ipai_post_message("Hello Slack!")

        self.assertTrue(result)
        mock_webhook.assert_called_once()

    # ------------------------------------------------------------------
    # S2 — SLACK_WEBHOOK_URL not set → UserError, no webhook call
    # ------------------------------------------------------------------

    def test_s2_no_webhook_url_raises_user_error(self):
        """No SLACK_WEBHOOK_URL → UserError raised before post_webhook called."""
        mock_webhook = MagicMock()

        with patch.dict(os.environ, {"SLACK_WEBHOOK_URL": ""}, clear=False):
            with patch(_PATCH_WEBHOOK, mock_webhook):
                with self.assertRaises(UserError) as ctx:
                    self.connector._ipai_post_message("Should not reach Slack")

        mock_webhook.assert_not_called()
        self.assertIn("SLACK_WEBHOOK_URL", str(ctx.exception))

    # ------------------------------------------------------------------
    # S3 — post_webhook raises HTTPError → UserError propagates
    # ------------------------------------------------------------------

    def test_s3_http_error_raises_user_error(self):
        """post_webhook raises HTTPError → _ipai_post_message wraps as UserError."""
        http_error = _requests_lib.HTTPError("HTTP 403: Forbidden")

        with patch.dict(os.environ, _SLACK_ENV):
            with patch(_PATCH_WEBHOOK, side_effect=http_error):
                with self.assertRaises(UserError) as ctx:
                    self.connector._ipai_post_message("Test message")

        self.assertIn("403", str(ctx.exception))

    # ------------------------------------------------------------------
    # S4 — channel kwarg forwarded in payload passed to post_webhook
    # ------------------------------------------------------------------

    def test_s4_channel_forwarded_in_payload(self):
        """channel kwarg is included in the payload dict passed to post_webhook."""
        captured_payload = {}

        def capture_payload(url, payload, **kwargs):
            captured_payload.update(payload)

        with patch.dict(os.environ, _SLACK_ENV):
            with patch(_PATCH_WEBHOOK, side_effect=capture_payload):
                self.connector._ipai_post_message("Hello!", channel="#general")

        self.assertEqual(captured_payload.get("text"), "Hello!")
        self.assertEqual(captured_payload.get("channel"), "#general")

    # ------------------------------------------------------------------
    # S5 — _ipai_slack_enabled() returns False when env var absent
    # ------------------------------------------------------------------

    def test_s5_slack_disabled_when_no_env(self):
        """_ipai_slack_enabled() returns False when SLACK_WEBHOOK_URL is absent."""
        with patch.dict(os.environ, {"SLACK_WEBHOOK_URL": ""}, clear=False):
            self.assertFalse(self.connector._ipai_slack_enabled())
