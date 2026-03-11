# -*- coding: utf-8 -*-
"""
Maintenance Equipment Integration - IPAI Event Emission
Emit events to Supabase integration bus for asset booking lifecycle

Note: This assumes a custom asset booking model that extends maintenance.equipment
If using standard Odoo maintenance, adapt hooks to your actual booking workflow
"""

from datetime import timedelta
from odoo import models, fields, api
from odoo.addons.ipai_enterprise_bridge.utils.ipai_webhook import send_ipai_event
import logging

_logger = logging.getLogger(__name__)


class MaintenanceEquipmentIntegration(models.Model):
    _inherit = 'maintenance.equipment'

    def action_reserve_asset(self):
        """
        Custom action: Reserve asset for use
        Emits asset.reserved event

        This is a placeholder - implement actual reservation logic based on your workflow
        """
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            _logger.warning("IPAI webhook not configured - skipping event emission")
            return

        for equipment in self:
            event = {
                "event_type": "asset.reserved",
                "aggregate_type": "asset_booking",
                "aggregate_id": str(equipment.id),
                "payload": {
                    "booking_id": equipment.id,  # Or use separate booking record ID
                    "asset_id": equipment.id,
                    "asset_name": equipment.name,
                    "asset_category": equipment.category_id.name if equipment.category_id else None,
                    "reserved_by": self.env.user.id,
                    "reserved_by_name": self.env.user.name,
                    "reserved_from": fields.Datetime.now().isoformat(),
                    "reserved_to": (fields.Datetime.now() + timedelta(days=7)).isoformat(),  # Default 7-day booking
                    "purpose": "",  # Add custom field if needed
                    "booking_state": "reserved",
                }
            }

            idempotency_key = f"asset.reserved:{equipment.id}:{fields.Datetime.now().timestamp()}"

            try:
                send_ipai_event(webhook_url, webhook_secret, event, idempotency_key=idempotency_key)
                _logger.info(f"✅ Emitted asset.reserved event for asset #{equipment.id}")
            except Exception as e:
                _logger.error(f"❌ Failed to emit asset.reserved event: {e}")

    def action_checkout_asset(self):
        """
        Custom action: Check out asset (physical handover)
        Emits asset.checked_out event
        """
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            return

        for equipment in self:
            event = {
                "event_type": "asset.checked_out",
                "aggregate_type": "asset_booking",
                "aggregate_id": str(equipment.id),
                "payload": {
                    "booking_id": equipment.id,
                    "asset_id": equipment.id,
                    "asset_name": equipment.name,
                    "checked_out_by": self.env.user.name,
                    "checked_out_at": fields.Datetime.now().isoformat(),
                    "booking_state": "checked_out",
                }
            }

            idempotency_key = f"asset.checked_out:{equipment.id}:{fields.Datetime.now().timestamp()}"

            try:
                send_ipai_event(webhook_url, webhook_secret, event, idempotency_key=idempotency_key)
                _logger.info(f"✅ Emitted asset.checked_out event for asset #{equipment.id}")
            except Exception as e:
                _logger.error(f"❌ Failed to emit asset.checked_out event: {e}")

    def action_checkin_asset(self):
        """
        Custom action: Check in asset (return)
        Emits asset.checked_in event
        """
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            return

        for equipment in self:
            event = {
                "event_type": "asset.checked_in",
                "aggregate_type": "asset_booking",
                "aggregate_id": str(equipment.id),
                "payload": {
                    "booking_id": equipment.id,
                    "asset_id": equipment.id,
                    "asset_name": equipment.name,
                    "checked_in_by": self.env.user.name,
                    "checked_in_at": fields.Datetime.now().isoformat(),
                    "booking_state": "returned",
                }
            }

            idempotency_key = f"asset.checked_in:{equipment.id}:{fields.Datetime.now().timestamp()}"

            try:
                send_ipai_event(webhook_url, webhook_secret, event, idempotency_key=idempotency_key)
                _logger.info(f"✅ Emitted asset.checked_in event for asset #{equipment.id}")
            except Exception as e:
                _logger.error(f"❌ Failed to emit asset.checked_in event: {e}")

    @api.model
    def _cron_detect_overdue_bookings(self):
        """
        Cron job to detect overdue asset bookings
        Emits asset.overdue event

        Run this cron daily to check for overdue bookings
        """
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            return

        # TODO: Implement actual overdue booking detection logic
        # This is a placeholder - adapt to your booking model

        _logger.info("Overdue booking detection cron completed")
