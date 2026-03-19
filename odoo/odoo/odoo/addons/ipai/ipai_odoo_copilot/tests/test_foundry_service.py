# -*- coding: utf-8 -*-

from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestFoundryService(TransactionCase):
    """Tests for ipai.foundry.service AbstractModel."""

    def setUp(self):
        super().setUp()
        self.service = self.env["ipai.foundry.service"]
        self.ICP = self.env["ir.config_parameter"].sudo()

    # ------------------------------------------------------------------
    # Config helpers
    # ------------------------------------------------------------------

    def test_get_settings_returns_defaults(self):
        """_get_settings returns expected keys with sane defaults."""
        settings = self.service._get_settings()
        self.assertIn("enabled", settings)
        self.assertIn("api_endpoint", settings)
        self.assertIn("project", settings)
        self.assertIn("agent_name", settings)
        self.assertIn("model", settings)
        self.assertIn("search_service", settings)
        self.assertIn("search_connection", settings)
        self.assertIn("search_index", settings)
        self.assertIn("memory_enabled", settings)
        self.assertIn("read_only_mode", settings)

    def test_get_settings_reads_params(self):
        """_get_settings reads from ir.config_parameter."""
        self.ICP.set_param("ipai_odoo_copilot.foundry_project", "test-proj")
        settings = self.service._get_settings()
        self.assertEqual(settings["project"], "test-proj")

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def test_auth_mode_none_without_env(self):
        """Without IMDS or env key, auth mode is 'none'."""
        with patch.dict("os.environ", {}, clear=True):
            mode, secret = self.service._get_auth_mode()
        self.assertEqual(mode, "none")
        self.assertEqual(secret, "")

    def test_auth_mode_api_key_from_env(self):
        """AZURE_FOUNDRY_API_KEY env var produces api-key mode."""
        with patch.dict(
            "os.environ", {"AZURE_FOUNDRY_API_KEY": "test-key-123"}
        ):
            mode, secret = self.service._get_auth_mode()
        self.assertEqual(mode, "api-key")
        self.assertEqual(secret, "test-key-123")

    def test_auth_headers_api_key(self):
        """api-key mode returns correct header shape."""
        with patch.dict(
            "os.environ", {"AZURE_FOUNDRY_API_KEY": "k"}
        ):
            headers, mode = self.service._get_auth_headers()
        self.assertEqual(mode, "api-key")
        self.assertIn("api-key", headers)
        self.assertEqual(headers["api-key"], "k")

    # ------------------------------------------------------------------
    # HTTP classification
    # ------------------------------------------------------------------

    def test_classify_success(self):
        ok, msg = self.service._classify_http_status(200, None, "api-key")
        self.assertTrue(ok)

    def test_classify_401(self):
        ok, msg = self.service._classify_http_status(
            401, "Unauthorized", "api-key"
        )
        self.assertFalse(ok)
        self.assertIn("401", msg)

    def test_classify_unreachable(self):
        ok, msg = self.service._classify_http_status(
            0, "Connection refused", "none"
        )
        self.assertFalse(ok)
        self.assertIn("Unreachable", msg)

    # ------------------------------------------------------------------
    # test_connection
    # ------------------------------------------------------------------

    def test_connection_disabled(self):
        """test_connection fails when addon is disabled."""
        self.ICP.set_param("ipai_odoo_copilot.foundry_enabled", "False")
        ok, msg = self.service.test_connection()
        self.assertFalse(ok)
        self.assertIn("disabled", msg.lower())

    def test_connection_missing_config(self):
        """test_connection fails when required config is missing."""
        self.ICP.set_param("ipai_odoo_copilot.foundry_enabled", "True")
        self.ICP.set_param("ipai_odoo_copilot.foundry_api_endpoint", "")
        self.ICP.set_param("ipai_odoo_copilot.foundry_project", "")
        self.ICP.set_param("ipai_odoo_copilot.foundry_agent_name", "")
        self.ICP.set_param("ipai_odoo_copilot.foundry_model", "")
        ok, msg = self.service.test_connection()
        self.assertFalse(ok)
        self.assertIn("Missing", msg)

    def test_connection_no_auth(self):
        """test_connection fails when no auth is available."""
        self.ICP.set_param("ipai_odoo_copilot.foundry_enabled", "True")
        self.ICP.set_param(
            "ipai_odoo_copilot.foundry_api_endpoint",
            "https://example.services.ai.azure.com",
        )
        self.ICP.set_param("ipai_odoo_copilot.foundry_project", "proj")
        self.ICP.set_param("ipai_odoo_copilot.foundry_agent_name", "agent")
        self.ICP.set_param("ipai_odoo_copilot.foundry_model", "gpt-4.1")
        with patch.dict("os.environ", {}, clear=True):
            ok, msg = self.service.test_connection()
        self.assertFalse(ok)
        self.assertIn("No auth", msg)
