"""
Odoo TransactionCase smoke tests for ipai_llm_supabase_bridge.

Runs via Odoo's test runner (not plain pytest):
    python odoo-bin --test-enable --test-tags ipai_llm_supabase_bridge -d odoo_dev

Test coverage targets
---------------------
S1  Models registered          → ipai.bridge.config and ipai.bridge.event exist in env
S2  Config fields present      → webhook_url, webhook_secret, enabled, max_retries
S3  Event fields present       → event_type, status, idempotency_key, payload
S4  _emit() is no-op disabled  → bridge disabled → _emit() returns empty recordset;
                                  NO outbound network calls made

IMPORTANT: All tests patch or disable outbound HTTP.  No test may reach the
           network.  If requests.post is ever called, the test suite must fail.
"""

from unittest.mock import patch

from odoo.tests import TransactionCase, tagged


# ---------------------------------------------------------------------------
# Patch boundary: block all real network calls for the entire module
# ---------------------------------------------------------------------------

_PATCH_REQUESTS_POST = "requests.post"


@tagged("ipai_llm_supabase_bridge", "-at_install", "post_install")
class TestInstallSmoke(TransactionCase):
    """Install-time smoke tests — no network calls allowed."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure bridge is disabled for the entire test class so _emit()
        # never tries to reach a real Supabase endpoint.
        cls.env["ir.config_parameter"].sudo().set_param(
            "ipai_llm_supabase_bridge.enabled", "False"
        )

    # ------------------------------------------------------------------
    # S1 — Both models exist in env
    # ------------------------------------------------------------------

    def test_s1_models_registered(self):
        """ipai.bridge.config and ipai.bridge.event models exist in env."""
        self.assertIn("ipai.bridge.config", self.env)
        self.assertIn("ipai.bridge.event", self.env)

    # ------------------------------------------------------------------
    # S2 — Config model has expected fields
    # ------------------------------------------------------------------

    def test_s2_config_fields_present(self):
        """ipai.bridge.config has webhook_url, webhook_secret, enabled, max_retries."""
        config_model = self.env["ipai.bridge.config"]
        expected_fields = {
            "webhook_url",
            "webhook_secret",
            "enabled",
            "max_retries",
            "retry_backoff_base",
            "batch_size",
        }
        model_fields = set(config_model._fields.keys())
        missing = expected_fields - model_fields
        self.assertFalse(
            missing,
            f"ipai.bridge.config is missing fields: {missing}",
        )

    # ------------------------------------------------------------------
    # S3 — Event model has expected fields
    # ------------------------------------------------------------------

    def test_s3_event_fields_present(self):
        """ipai.bridge.event has event_type, status, idempotency_key, payload."""
        event_model = self.env["ipai.bridge.event"]
        expected_fields = {
            "event_type",
            "status",
            "idempotency_key",
            "payload",
            "attempts",
            "next_retry_at",
            "res_model",
            "res_id",
            "odoo_db",
        }
        model_fields = set(event_model._fields.keys())
        missing = expected_fields - model_fields
        self.assertFalse(
            missing,
            f"ipai.bridge.event is missing fields: {missing}",
        )

    # ------------------------------------------------------------------
    # S4 — _emit() returns empty recordset when bridge is disabled;
    #      requests.post must never be called
    # ------------------------------------------------------------------

    def test_s4_emit_noop_when_disabled(self):
        """_emit() is a no-op and makes no network calls when bridge is disabled."""
        with patch(_PATCH_REQUESTS_POST) as mock_post:
            result = self.env["ipai.bridge.event"]._emit(
                event_type="tool.call",
                payload={"tool": "test_tool", "args": {}},
                idempotency_key="smoke-test-disabled-key",
            )

        # Must return empty recordset (not raise, not create a row)
        self.assertFalse(result, "Expected empty recordset; got a record")
        mock_post.assert_not_called()
