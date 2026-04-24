# -*- coding: utf-8 -*-
"""
test_install.py — Verifies that ipai_pulser_chat installs cleanly and
that its default ir.config_parameter records are present with the
expected default values.

Run with:
    odoo-bin -d test_ipai_pulser_chat --test-enable -i ipai_pulser_chat
"""

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("ipai", "ipai_pulser_chat", "-at_install", "post_install")
class TestInstall(TransactionCase):
    """Module install smoke tests."""

    def test_config_params_exist(self):
        """ir.config_parameter defaults are seeded by data/ir_config_parameter.xml."""
        ICP = self.env["ir.config_parameter"].sudo()
        enabled = ICP.get_param("ipai.pulser_chat.enabled")
        backend_url = ICP.get_param("ipai.pulser_chat.backend_url")
        timeout = ICP.get_param("ipai.pulser_chat.timeout_seconds")
        self.assertEqual(enabled, "False", "Default enabled must be 'False'")
        self.assertIsNotNone(backend_url, "backend_url param must exist")
        self.assertEqual(timeout, "30", "Default timeout must be '30'")

    def test_controller_importable(self):
        """Controller module must be importable without errors."""
        from odoo.addons.ipai_pulser_chat.controllers import pulser_chat  # noqa: F401

    def test_settings_model_fields_exist(self):
        """res.config.settings must expose all three Pulser Chat fields."""
        ResConfig = self.env["res.config.settings"]
        field_names = ResConfig.fields_get()
        for field in (
            "ipai_pulser_chat_enabled",
            "ipai_pulser_chat_backend_url",
            "ipai_pulser_chat_timeout_seconds",
        ):
            self.assertIn(
                field,
                field_names,
                f"Expected field '{field}' on res.config.settings",
            )
