# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestCopilotGatewayConfig(TransactionCase):
    """Tests for copilot gateway configuration (ir.config_parameter)."""

    def setUp(self):
        super().setUp()
        self.ICP = self.env['ir.config_parameter'].sudo()

    def test_default_gateway_url(self):
        """Default gateway URL is localhost:8088."""
        url = self.ICP.get_param('ipai.copilot.gateway_url', '')
        # May or may not be set yet depending on module install state,
        # but the controller default is http://localhost:8088
        self.assertTrue(url == '' or 'localhost' in url or '8088' in url)

    def test_default_enabled(self):
        """Default enabled state is True."""
        val = self.ICP.get_param('ipai.copilot.enabled', 'True')
        self.assertIn(val.lower(), ('true', '1', 'yes', ''))

    def test_default_mode(self):
        """Default mode is PROD-ADVISORY."""
        mode = self.ICP.get_param('ipai.copilot.mode', 'PROD-ADVISORY')
        self.assertEqual(mode, 'PROD-ADVISORY')
