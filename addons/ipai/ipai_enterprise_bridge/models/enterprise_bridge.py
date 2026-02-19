# -*- coding: utf-8 -*-
"""
Enterprise Bridge - CE/OCA Compatibility Layer

This module provides Enterprise-compatible interfaces that route to
OCA alternatives or provide graceful stubs.
"""
from odoo import api, fields, models


class EnterpriseBridgeConfig(models.Model):
    """Configuration for Enterprise feature bridges."""

    _name = "ipai.enterprise.bridge.config"
    _description = "Enterprise Bridge Configuration"

    name = fields.Char(
        string="Feature Name",
        required=True,
        help="Name of the Enterprise feature being bridged",
    )
    feature_code = fields.Char(
        string="Feature Code",
        required=True,
        help="Technical code for the feature (e.g., 'studio', 'planning')",
    )
    oca_alternative = fields.Char(
        string="OCA Alternative",
        help="OCA module providing similar functionality",
    )
    bridge_mode = fields.Selection(
        [
            ("stub", "Stub (No-op)"),
            ("oca", "OCA Alternative"),
            ("custom", "Custom Implementation"),
            ("disabled", "Disabled"),
        ],
        string="Bridge Mode",
        default="stub",
        required=True,
    )
    is_active = fields.Boolean(
        string="Active",
        default=True,
    )
    notes = fields.Text(
        string="Notes",
        help="Implementation notes or limitations",
    )

    _sql_constraints = [
        (
            "feature_code_unique",
            "UNIQUE(feature_code)",
            "Feature code must be unique.",
        ),
    ]

    @api.model
    def get_bridge_mode(self, feature_code):
        """Get the bridge mode for a specific feature.

        Args:
            feature_code: Technical code of the feature

        Returns:
            str: Bridge mode ('stub', 'oca', 'custom', 'disabled')
        """
        config = self.search(
            [("feature_code", "=", feature_code), ("is_active", "=", True)],
            limit=1,
        )
        return config.bridge_mode if config else "stub"

    @api.model
    def is_feature_available(self, feature_code):
        """Check if a bridged feature is available.

        Args:
            feature_code: Technical code of the feature

        Returns:
            bool: True if feature has an active bridge (not disabled)
        """
        mode = self.get_bridge_mode(feature_code)
        return mode != "disabled"


class IAPBridgeMixin(models.AbstractModel):
    """Mixin for models that need IAP bypass functionality.

    Provides methods to check IAP availability and route to
    alternative implementations.
    """

    _name = "ipai.iap.bridge.mixin"
    _description = "IAP Bridge Mixin"

    @api.model
    def _check_iap_service(self, service_name):
        """Check if an IAP service is available.

        In CE+OCA stack, this always returns False and routes
        to configured alternatives.

        Args:
            service_name: Name of the IAP service

        Returns:
            bool: Always False in CE+OCA mode
        """
        return False

    @api.model
    def _get_iap_alternative(self, service_name):
        """Get the configured alternative for an IAP service.

        Args:
            service_name: Name of the IAP service

        Returns:
            str: Alternative service configuration or None
        """
        # Map IAP services to alternatives
        alternatives = {
            "sms": "direct_sms",  # Use direct SMS gateway
            "mail": "direct_smtp",  # Use direct SMTP
            "partner_autocomplete": "manual",  # Manual entry
            "snailmail": "disabled",  # No physical mail
            "ocr": "manual",  # Manual data entry
        }
        return alternatives.get(service_name)
