# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestResConfigSettings(TransactionCase):
    """Tests for res.config.settings IPAI Copilot fields."""

    def setUp(self):
        super().setUp()
        self.ICP = self.env["ir.config_parameter"].sudo()

    def test_fields_exist(self):
        """All IPAI Copilot fields are present on res.config.settings."""
        settings = self.env["res.config.settings"].create({})
        expected_fields = [
            "ipai_foundry_enabled",
            "ipai_foundry_endpoint",
            "ipai_foundry_api_endpoint",
            "ipai_foundry_project",
            "ipai_foundry_agent_name",
            "ipai_foundry_model",
            "ipai_foundry_search_service",
            "ipai_foundry_search_connection",
            "ipai_foundry_search_index",
            "ipai_foundry_memory_enabled",
            "ipai_foundry_read_only_mode",
        ]
        for field in expected_fields:
            self.assertIn(
                field,
                settings._fields,
                f"Field {field} missing from res.config.settings",
            )

    def test_defaults(self):
        """Canonical defaults are set correctly."""
        settings = self.env["res.config.settings"].create({})
        self.assertFalse(settings.ipai_foundry_enabled)
        self.assertTrue(settings.ipai_foundry_read_only_mode)
        self.assertFalse(settings.ipai_foundry_memory_enabled)
        self.assertEqual(settings.ipai_foundry_model, "gpt-4.1")
        self.assertEqual(
            settings.ipai_foundry_agent_name, "ipai-odoo-copilot-azure"
        )
        self.assertEqual(settings.ipai_foundry_project, "data-intel-ph")

    def test_config_parameter_persistence(self):
        """Settings persist through ir.config_parameter."""
        settings = self.env["res.config.settings"].create(
            {"ipai_foundry_project": "test-project-123"}
        )
        settings.set_values()
        val = self.ICP.get_param("ipai_odoo_copilot.foundry_project")
        self.assertEqual(val, "test-project-123")

    def test_action_test_connection_returns_notification(self):
        """action_test_foundry_connection returns display_notification."""
        settings = self.env["res.config.settings"].create({})
        result = settings.action_test_foundry_connection()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")
        self.assertIn("message", result["params"])

    def test_action_ensure_agent_returns_notification(self):
        """action_ensure_foundry_agent returns display_notification."""
        settings = self.env["res.config.settings"].create({})
        result = settings.action_ensure_foundry_agent()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")

    def test_action_open_portal_no_endpoint(self):
        """action_open_foundry_portal warns when no endpoint configured."""
        self.ICP.set_param("ipai_odoo_copilot.foundry_endpoint", "")
        settings = self.env["res.config.settings"].create({})
        result = settings.action_open_foundry_portal()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("warning", result["params"]["type"])

    def test_action_open_portal_with_endpoint(self):
        """action_open_foundry_portal opens URL when endpoint is set."""
        self.ICP.set_param(
            "ipai_odoo_copilot.foundry_endpoint", "https://ai.azure.com"
        )
        settings = self.env["res.config.settings"].create({})
        result = settings.action_open_foundry_portal()
        self.assertEqual(result["type"], "ir.actions.act_url")
        self.assertEqual(result["url"], "https://ai.azure.com")
