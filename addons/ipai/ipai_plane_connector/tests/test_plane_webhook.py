# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""
Tests for Plane webhook signature verification and delivery deduplication.

Mock boundary:
    patch("odoo.addons.ipai_plane_connector.utils.plane_webhook.verify_plane_signature")

Test coverage targets
---------------------
W1  Valid HMAC signature         → verify_plane_signature returns True
W2  Invalid HMAC signature       → verify_plane_signature returns False
W3  Missing inputs               → returns False (no crash)
W4  Connector webhook verify     → _plane_verify_webhook delegates correctly
W5  Connector no secret config   → UserError raised
W6  Delivery dedup: new          → _plane_is_duplicate_delivery returns False
W7  Delivery dedup: duplicate    → _plane_is_duplicate_delivery returns True
W8  Delivery record creation     → _plane_record_delivery creates record
W9  SQL constraint on dup ID     → IntegrityError on duplicate delivery_id
W10 _plane_enabled check         → True when all params set, False otherwise
"""

import hashlib
import hmac as hmac_mod
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_WEBHOOK_SECRET = "test-webhook-secret-abc123"
_PAYLOAD = b'{"event":"issue.created","data":{"id":"iss-1"}}'

_PATCH_VERIFY = (
    "odoo.addons.ipai_plane_connector.utils.plane_webhook"
    ".verify_plane_signature"
)


def _compute_signature(secret, payload):
    """Compute expected HMAC-SHA256 hex digest."""
    return hmac_mod.new(
        secret.encode("utf-8") if isinstance(secret, str) else secret,
        payload if isinstance(payload, bytes) else payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# ---------------------------------------------------------------------------
# Pure-Python verification tests
# ---------------------------------------------------------------------------


@tagged("ipai_plane_connector", "-at_install", "post_install")
class TestPlaneWebhookSignature(TransactionCase):
    """Layer-1 tests for verify_plane_signature (pure-Python)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    # ------------------------------------------------------------------
    # W1 — Valid signature
    # ------------------------------------------------------------------

    def test_w1_valid_signature(self):
        """Correct HMAC-SHA256 signature returns True."""
        from odoo.addons.ipai_plane_connector.utils.plane_webhook import (
            verify_plane_signature,
        )
        sig = _compute_signature(_WEBHOOK_SECRET, _PAYLOAD)
        self.assertTrue(
            verify_plane_signature(_WEBHOOK_SECRET, _PAYLOAD, sig),
        )

    # ------------------------------------------------------------------
    # W2 — Invalid signature
    # ------------------------------------------------------------------

    def test_w2_invalid_signature(self):
        """Wrong signature returns False."""
        from odoo.addons.ipai_plane_connector.utils.plane_webhook import (
            verify_plane_signature,
        )
        self.assertFalse(
            verify_plane_signature(
                _WEBHOOK_SECRET, _PAYLOAD, "badhexdigest",
            ),
        )

    # ------------------------------------------------------------------
    # W3 — Missing inputs
    # ------------------------------------------------------------------

    def test_w3_missing_secret(self):
        """Empty/None secret returns False without crashing."""
        from odoo.addons.ipai_plane_connector.utils.plane_webhook import (
            verify_plane_signature,
        )
        self.assertFalse(
            verify_plane_signature("", _PAYLOAD, "abc"),
        )
        self.assertFalse(
            verify_plane_signature(None, _PAYLOAD, "abc"),
        )

    def test_w3_missing_payload(self):
        """Empty/None payload returns False without crashing."""
        from odoo.addons.ipai_plane_connector.utils.plane_webhook import (
            verify_plane_signature,
        )
        self.assertFalse(
            verify_plane_signature(_WEBHOOK_SECRET, b"", "abc"),
        )
        self.assertFalse(
            verify_plane_signature(_WEBHOOK_SECRET, None, "abc"),
        )

    def test_w3_missing_signature_header(self):
        """Empty/None signature header returns False."""
        from odoo.addons.ipai_plane_connector.utils.plane_webhook import (
            verify_plane_signature,
        )
        self.assertFalse(
            verify_plane_signature(_WEBHOOK_SECRET, _PAYLOAD, ""),
        )
        self.assertFalse(
            verify_plane_signature(_WEBHOOK_SECRET, _PAYLOAD, None),
        )

    # ------------------------------------------------------------------
    # W4 — String payload
    # ------------------------------------------------------------------

    def test_w4_string_payload(self):
        """String payload is accepted and verified correctly."""
        from odoo.addons.ipai_plane_connector.utils.plane_webhook import (
            verify_plane_signature,
        )
        payload_str = _PAYLOAD.decode("utf-8")
        sig = _compute_signature(_WEBHOOK_SECRET, payload_str)
        self.assertTrue(
            verify_plane_signature(_WEBHOOK_SECRET, payload_str, sig),
        )


# ---------------------------------------------------------------------------
# Odoo model-level tests (connector + dedup)
# ---------------------------------------------------------------------------


@tagged("ipai_plane_connector", "-at_install", "post_install")
class TestPlaneWebhookConnector(TransactionCase):
    """Layer-2 tests for ipai.plane.connector webhook + dedup helpers."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.connector = self.env["ipai.plane.connector"]
        self.Delivery = self.env["plane.webhook.delivery"]

    # ------------------------------------------------------------------
    # W5 — _plane_verify_webhook with no secret configured
    # ------------------------------------------------------------------

    def test_w5_no_secret_raises_user_error(self):
        """_plane_verify_webhook raises UserError when secret is missing."""
        # Ensure no webhook secret is set
        self.env["ir.config_parameter"].sudo().set_param(
            "plane.webhook_secret", False,
        )
        with self.assertRaises(UserError):
            self.connector._plane_verify_webhook(
                {"X-Plane-Signature": "abc"}, b"body",
            )

    # ------------------------------------------------------------------
    # W5b — _plane_verify_webhook delegates to verify_plane_signature
    # ------------------------------------------------------------------

    def test_w5b_verify_webhook_delegates(self):
        """_plane_verify_webhook calls verify_plane_signature correctly."""
        self.env["ir.config_parameter"].sudo().set_param(
            "plane.webhook_secret", _WEBHOOK_SECRET,
        )
        sig = _compute_signature(_WEBHOOK_SECRET, _PAYLOAD)
        result = self.connector._plane_verify_webhook(
            {"X-Plane-Signature": sig}, _PAYLOAD,
        )
        self.assertTrue(result)

    def test_w5c_verify_webhook_bad_sig(self):
        """_plane_verify_webhook returns False for bad signature."""
        self.env["ir.config_parameter"].sudo().set_param(
            "plane.webhook_secret", _WEBHOOK_SECRET,
        )
        result = self.connector._plane_verify_webhook(
            {"X-Plane-Signature": "invalid"}, _PAYLOAD,
        )
        self.assertFalse(result)

    # ------------------------------------------------------------------
    # W6 — Delivery dedup: new delivery
    # ------------------------------------------------------------------

    def test_w6_new_delivery_not_duplicate(self):
        """New delivery_id is not a duplicate."""
        self.assertFalse(
            self.connector._plane_is_duplicate_delivery("new-id-001"),
        )

    def test_w6_empty_delivery_id(self):
        """Empty/falsy delivery_id is not considered duplicate."""
        self.assertFalse(
            self.connector._plane_is_duplicate_delivery(""),
        )
        self.assertFalse(
            self.connector._plane_is_duplicate_delivery(None),
        )

    # ------------------------------------------------------------------
    # W7 — Delivery dedup: existing delivery
    # ------------------------------------------------------------------

    def test_w7_existing_delivery_is_duplicate(self):
        """Recorded delivery_id is detected as duplicate."""
        self.connector._plane_record_delivery(
            "dup-id-001", event_type="issue.created",
        )
        self.assertTrue(
            self.connector._plane_is_duplicate_delivery("dup-id-001"),
        )

    # ------------------------------------------------------------------
    # W8 — Delivery record creation
    # ------------------------------------------------------------------

    def test_w8_record_delivery_creates_record(self):
        """_plane_record_delivery creates a plane.webhook.delivery record."""
        record = self.connector._plane_record_delivery(
            "rec-001", event_type="cycle.updated",
        )
        self.assertTrue(record.exists())
        self.assertEqual(record.delivery_id, "rec-001")
        self.assertEqual(record.event_type, "cycle.updated")
        self.assertFalse(record.processed)

    # ------------------------------------------------------------------
    # W9 — SQL unique constraint
    # ------------------------------------------------------------------

    def test_w9_duplicate_delivery_id_raises(self):
        """Duplicate delivery_id violates SQL constraint."""
        self.Delivery.sudo().create({
            "delivery_id": "unique-id-001",
            "event_type": "issue.created",
        })
        with self.assertRaises(Exception):
            self.Delivery.sudo().create({
                "delivery_id": "unique-id-001",
                "event_type": "issue.updated",
            })
            # Force flush to trigger the SQL constraint
            self.env.cr.flush()

    # ------------------------------------------------------------------
    # W10 — _plane_enabled check
    # ------------------------------------------------------------------

    def test_w10_enabled_when_all_params_set(self):
        """_plane_enabled returns True when all params are configured."""
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("plane.base_url", "https://api.plane.so")
        params.set_param("plane.api_key", "test-api-key")
        params.set_param("plane.workspace_slug", "testworkspace")
        self.assertTrue(self.connector._plane_enabled())

    def test_w10_disabled_when_api_key_missing(self):
        """_plane_enabled returns False when api_key is missing."""
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("plane.base_url", "https://api.plane.so")
        params.set_param("plane.api_key", False)
        params.set_param("plane.workspace_slug", "testworkspace")
        self.assertFalse(self.connector._plane_enabled())

    def test_w10_disabled_when_workspace_missing(self):
        """_plane_enabled returns False when workspace_slug is missing."""
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("plane.base_url", "https://api.plane.so")
        params.set_param("plane.api_key", "test-api-key")
        params.set_param("plane.workspace_slug", False)
        self.assertFalse(self.connector._plane_enabled())
