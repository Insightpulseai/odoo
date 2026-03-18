# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""
Tests for the Pulser universal JSON envelope contract.

Validates:
  - Required keys exist in success/error envelopes
  - Timestamps are ISO8601 UTC
  - Payload size < 32KB
  - Evidence always present
"""

import json
import time
from datetime import datetime, timezone

from odoo.tests.common import TransactionCase


class TestPulserEnvelope(TransactionCase):

    def setUp(self):
        super().setUp()
        self.intent_model = self.env["ipai.pulser.intent"]
        self.handlers = self.env["ipai.pulser.handlers"]

    def _make_mock_intent(self, intent_type="odoo.healthcheck"):
        """Build a mock intent dict as returned by the claim RPC."""
        return {
            "intent_id": 1,
            "run_id": "00000000-0000-0000-0000-000000000001",
            "request_id": "test-req-001",
            "intent_type": intent_type,
            "args": {},
            "claimed_at": datetime.now(timezone.utc).isoformat(),
        }

    # ── Success envelope ────────────────────────────────────────────────

    def test_success_envelope_has_required_keys(self):
        """Success envelope must have ok, intent, trace, data, evidence."""
        intent = self._make_mock_intent()
        data = self.handlers._dispatch("odoo.healthcheck", {})
        envelope = self.intent_model._build_envelope(intent, data, time.time())

        self.assertTrue(envelope["ok"])
        self.assertIn("intent", envelope)
        self.assertIn("trace", envelope)
        self.assertIn("data", envelope)
        self.assertIn("evidence", envelope)

        # Intent section
        self.assertIn("intent_id", envelope["intent"])
        self.assertIn("intent_type", envelope["intent"])
        self.assertIn("finished_at", envelope["intent"])
        self.assertIn("duration_ms", envelope["intent"])

        # Trace section
        self.assertIn("run_id", envelope["trace"])
        self.assertIn("correlation_id", envelope["trace"])

        # Evidence section
        self.assertIn("artifacts", envelope["evidence"])
        self.assertIn("links", envelope["evidence"])

    def test_success_envelope_timestamps_are_iso8601(self):
        """All timestamps must be ISO8601 UTC."""
        intent = self._make_mock_intent()
        data = self.handlers._dispatch("odoo.healthcheck", {})
        envelope = self.intent_model._build_envelope(intent, data, time.time())

        finished_at = envelope["intent"]["finished_at"]
        # Must parse without error
        parsed = datetime.fromisoformat(finished_at)
        self.assertIsNotNone(parsed)

    def test_success_envelope_size_under_32kb(self):
        """Total JSON payload must be under 32KB."""
        intent = self._make_mock_intent()
        data = self.handlers._dispatch("odoo.healthcheck", {})
        envelope = self.intent_model._build_envelope(intent, data, time.time())

        size = len(json.dumps(envelope).encode("utf-8"))
        self.assertLess(size, 32 * 1024, "Envelope exceeds 32KB limit")

    # ── Error envelope ──────────────────────────────────────────────────

    def test_error_envelope_has_required_keys(self):
        """Error envelope must have ok=False, error section, evidence."""
        intent = self._make_mock_intent()
        envelope = self.intent_model._build_error_envelope(
            intent,
            code="ODOO_EXEC_ERROR",
            message="Test error",
            details={"test": True},
            retryable=False,
            start_time=time.time(),
        )

        self.assertFalse(envelope["ok"])
        self.assertIn("error", envelope)
        self.assertIn("code", envelope["error"])
        self.assertIn("message", envelope["error"])
        self.assertIn("retryable", envelope["error"])
        self.assertIn("evidence", envelope)

    def test_error_envelope_no_data_key(self):
        """Error envelope must NOT have a 'data' key."""
        intent = self._make_mock_intent()
        envelope = self.intent_model._build_error_envelope(
            intent,
            code="TEST",
            message="fail",
            start_time=time.time(),
        )

        self.assertNotIn("data", envelope)

    # ── All handlers produce valid envelopes ────────────────────────────

    def test_all_handlers_produce_valid_envelopes(self):
        """Every registered handler must produce an envelope with all keys."""
        intent_types = [
            "odoo.healthcheck",
            "odoo.modules.status",
            "odoo.config.snapshot",
        ]

        for intent_type in intent_types:
            with self.subTest(intent_type=intent_type):
                intent = self._make_mock_intent(intent_type)
                data = self.handlers._dispatch(intent_type, {})
                envelope = self.intent_model._build_envelope(
                    intent, data, time.time()
                )

                self.assertTrue(envelope["ok"], intent_type)
                self.assertIsInstance(envelope["data"], dict)
                self.assertLess(
                    len(json.dumps(envelope).encode("utf-8")),
                    32 * 1024,
                    "%s exceeds 32KB" % intent_type,
                )
