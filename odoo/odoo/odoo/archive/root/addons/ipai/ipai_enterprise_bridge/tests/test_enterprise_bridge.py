# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase


class TestEnterpriseBridge(TransactionCase):
    """Test cases for Enterprise Bridge module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.BridgeConfig = cls.env["ipai.enterprise.bridge.config"]

    def test_bridge_config_creation(self):
        """Test creating a bridge configuration."""
        config = self.BridgeConfig.create(
            {
                "name": "Test Feature",
                "feature_code": "test_feature",
                "bridge_mode": "stub",
            }
        )
        self.assertEqual(config.name, "Test Feature")
        self.assertEqual(config.bridge_mode, "stub")

    def test_get_bridge_mode(self):
        """Test getting bridge mode for a feature."""
        self.BridgeConfig.create(
            {
                "name": "Test Feature",
                "feature_code": "test_mode",
                "bridge_mode": "oca",
                "is_active": True,
            }
        )
        mode = self.BridgeConfig.get_bridge_mode("test_mode")
        self.assertEqual(mode, "oca")

    def test_get_bridge_mode_nonexistent(self):
        """Test getting bridge mode for nonexistent feature."""
        mode = self.BridgeConfig.get_bridge_mode("nonexistent_feature")
        self.assertEqual(mode, "stub")

    def test_is_feature_available(self):
        """Test checking if feature is available."""
        self.BridgeConfig.create(
            {
                "name": "Available Feature",
                "feature_code": "available",
                "bridge_mode": "oca",
                "is_active": True,
            }
        )
        self.assertTrue(self.BridgeConfig.is_feature_available("available"))

    def test_is_feature_disabled(self):
        """Test checking disabled feature."""
        self.BridgeConfig.create(
            {
                "name": "Disabled Feature",
                "feature_code": "disabled",
                "bridge_mode": "disabled",
                "is_active": True,
            }
        )
        self.assertFalse(self.BridgeConfig.is_feature_available("disabled"))

    def test_unique_feature_code(self):
        """Test that feature codes must be unique."""
        self.BridgeConfig.create(
            {
                "name": "First Feature",
                "feature_code": "unique_test",
                "bridge_mode": "stub",
            }
        )
        with self.assertRaises(Exception):
            self.BridgeConfig.create(
                {
                    "name": "Duplicate Feature",
                    "feature_code": "unique_test",
                    "bridge_mode": "stub",
                }
            )
