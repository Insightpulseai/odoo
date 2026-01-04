# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024 InsightPulseAI
"""
Test cases for IPAI Master Control module.

Tests cover:
- Master Control configuration management
- Webhook emission (with mocked HTTP)
- Event enablement checks
- Work item payload construction
"""
from unittest.mock import MagicMock, patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "ipai_master_control")
class TestMasterControlConfig(TransactionCase):
    """Test Master Control configuration functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Mixin = cls.env["master.control.mixin"]
        cls.ICP = cls.env["ir.config_parameter"].sudo()

    def test_01_default_config_values(self):
        """Test default configuration values when not set."""
        # Clear any existing config
        self.ICP.set_param("master_control.webhook_url", "")
        self.ICP.set_param("master_control.enabled", "true")

        config = self.Mixin._get_master_control_config()

        self.assertEqual(config["webhook_url"], "")
        self.assertEqual(
            config["tenant_id"], "00000000-0000-0000-0000-000000000001"
        )
        self.assertTrue(config["enabled"])

    def test_02_config_from_parameters(self):
        """Test configuration loaded from system parameters."""
        self.ICP.set_param("master_control.webhook_url", "https://api.test.com")
        self.ICP.set_param("master_control.tenant_id", "test-tenant-123")
        self.ICP.set_param("master_control.enabled", "true")

        config = self.Mixin._get_master_control_config()

        self.assertEqual(config["webhook_url"], "https://api.test.com")
        self.assertEqual(config["tenant_id"], "test-tenant-123")
        self.assertTrue(config["enabled"])

    def test_03_config_disabled(self):
        """Test configuration when disabled."""
        self.ICP.set_param("master_control.enabled", "false")

        config = self.Mixin._get_master_control_config()

        self.assertFalse(config["enabled"])

    def test_04_event_enablement_settings(self):
        """Test event-specific enablement settings."""
        self.ICP.set_param("master_control.events.employee_hire", "true")
        self.ICP.set_param("master_control.events.employee_departure", "false")
        self.ICP.set_param("master_control.events.expense_submit", "true")
        self.ICP.set_param("master_control.events.purchase_large", "false")

        config = self.Mixin._get_master_control_config()

        self.assertTrue(config["events"]["employee_hire"])
        self.assertFalse(config["events"]["employee_departure"])
        self.assertTrue(config["events"]["expense_submit"])
        self.assertFalse(config["events"]["purchase_large"])


@tagged("post_install", "-at_install", "ipai_master_control")
class TestMasterControlMixin(TransactionCase):
    """Test Master Control Mixin webhook emission."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Mixin = cls.env["master.control.mixin"]
        cls.ICP = cls.env["ir.config_parameter"].sudo()

    def setUp(self):
        """Reset config before each test."""
        super().setUp()
        self.ICP.set_param("master_control.enabled", "true")
        self.ICP.set_param("master_control.webhook_url", "https://api.test.com")
        self.ICP.set_param("master_control.tenant_id", "test-tenant")

    def test_01_emit_disabled_when_not_enabled(self):
        """Test emit returns False when Master Control is disabled."""
        self.ICP.set_param("master_control.enabled", "false")

        result = self.Mixin._emit_work_item(
            source="test",
            source_ref="test:1",
            title="Test Work Item",
            lane="HR",
        )

        self.assertFalse(result)

    def test_02_emit_disabled_when_no_url(self):
        """Test emit returns False when webhook URL is not configured."""
        self.ICP.set_param("master_control.webhook_url", "")

        result = self.Mixin._emit_work_item(
            source="test",
            source_ref="test:1",
            title="Test Work Item",
            lane="HR",
        )

        self.assertFalse(result)

    @patch("odoo.addons.ipai_master_control.models.master_control_mixin.requests")
    def test_03_emit_builds_correct_payload(self, mock_requests):
        """Test emit constructs correct work item payload."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"work_item_id": "wi-123"}
        mock_requests.post.return_value = mock_response

        result = self.Mixin._emit_work_item(
            source="odoo_event",
            source_ref="hr.employee:42:hire",
            title="New Employee Onboarding",
            lane="HR",
            priority=2,
            payload={"employee_id": 42, "department": "Engineering"},
            tags=["onboarding", "new_hire"],
        )

        # Verify the call was made
        mock_requests.post.assert_called_once()

        # Check the payload
        call_args = mock_requests.post.call_args
        json_payload = call_args.kwargs["json"]

        self.assertEqual(json_payload["source"], "odoo_event")
        self.assertEqual(json_payload["source_ref"], "hr.employee:42:hire")
        self.assertEqual(json_payload["title"], "New Employee Onboarding")
        self.assertEqual(json_payload["lane"], "HR")
        self.assertEqual(json_payload["priority"], 2)
        self.assertEqual(json_payload["tenant_id"], "test-tenant")
        self.assertEqual(json_payload["payload"]["employee_id"], 42)
        self.assertIn("onboarding", json_payload["tags"])

    @patch("odoo.addons.ipai_master_control.models.master_control_mixin.requests")
    def test_04_emit_handles_successful_response(self, mock_requests):
        """Test emit returns result on successful webhook call."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "work_item_id": "wi-456",
            "status": "created",
        }
        mock_requests.post.return_value = mock_response

        result = self.Mixin._emit_work_item(
            source="test",
            source_ref="test:1",
            title="Test Item",
            lane="IT",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["work_item_id"], "wi-456")

    @patch("odoo.addons.ipai_master_control.models.master_control_mixin.requests")
    def test_05_emit_handles_failed_response(self, mock_requests):
        """Test emit returns False on failed webhook call."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_requests.post.return_value = mock_response

        result = self.Mixin._emit_work_item(
            source="test",
            source_ref="test:1",
            title="Test Item",
            lane="IT",
        )

        self.assertFalse(result)

    @patch("odoo.addons.ipai_master_control.models.master_control_mixin.requests")
    def test_06_emit_handles_network_error(self, mock_requests):
        """Test emit handles network exceptions gracefully."""
        mock_requests.post.side_effect = Exception("Connection refused")

        result = self.Mixin._emit_work_item(
            source="test",
            source_ref="test:1",
            title="Test Item",
            lane="IT",
        )

        self.assertFalse(result)

    @patch("odoo.addons.ipai_master_control.models.master_control_mixin.requests")
    def test_07_emit_uses_default_priority(self, mock_requests):
        """Test emit uses default priority of 3 when not specified."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"work_item_id": "wi-789"}
        mock_requests.post.return_value = mock_response

        self.Mixin._emit_work_item(
            source="test",
            source_ref="test:1",
            title="Test Item",
            lane="FIN",
        )

        call_args = mock_requests.post.call_args
        json_payload = call_args.kwargs["json"]

        self.assertEqual(json_payload["priority"], 3)

    def test_08_is_event_enabled_when_enabled(self):
        """Test is_event_enabled returns True for enabled events."""
        self.ICP.set_param("master_control.enabled", "true")
        self.ICP.set_param("master_control.events.employee_hire", "true")

        result = self.Mixin._is_event_enabled("employee_hire")

        self.assertTrue(result)

    def test_09_is_event_enabled_when_disabled(self):
        """Test is_event_enabled returns False for disabled events."""
        self.ICP.set_param("master_control.enabled", "true")
        self.ICP.set_param("master_control.events.employee_departure", "false")

        result = self.Mixin._is_event_enabled("employee_departure")

        self.assertFalse(result)

    def test_10_is_event_enabled_when_master_disabled(self):
        """Test is_event_enabled returns False when master control is disabled."""
        self.ICP.set_param("master_control.enabled", "false")
        self.ICP.set_param("master_control.events.employee_hire", "true")

        result = self.Mixin._is_event_enabled("employee_hire")

        self.assertFalse(result)

    def test_11_is_event_enabled_unknown_event(self):
        """Test is_event_enabled returns False for unknown events."""
        self.ICP.set_param("master_control.enabled", "true")

        result = self.Mixin._is_event_enabled("unknown_event_type")

        self.assertFalse(result)
