# -*- coding: utf-8 -*-
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""
Maintenance Equipment Integration - Event Emission for Supabase Integration Bus

Emits events when equipment/asset lifecycle changes occur:
- asset.reserved: Equipment reserved for use
- asset.checked_out: Equipment checked out
- asset.checked_in: Equipment returned
- asset.overdue: Equipment overdue for return
"""
import hashlib
import hmac
import json
import logging
import time

import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MaintenanceEquipmentIntegration(models.Model):
    """Extend maintenance.equipment with integration event emission."""

    _inherit = "maintenance.equipment"

    # Asset tracking fields
    asset_status = fields.Selection(
        [
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("checked_out", "Checked Out"),
            ("maintenance", "In Maintenance"),
        ],
        string="Asset Status",
        default="available",
        tracking=True,
    )
    assigned_employee_id = fields.Many2one(
        "hr.employee",
        string="Assigned To",
        tracking=True,
    )
    checkout_date = fields.Date(string="Checkout Date")
    expected_return_date = fields.Date(string="Expected Return Date")

    # Integration tracking
    integration_last_event = fields.Char(
        string="Last Integration Event",
        readonly=True,
        copy=False,
    )
    integration_last_event_at = fields.Datetime(
        string="Last Event At",
        readonly=True,
        copy=False,
    )

    def _get_integration_config(self):
        """Get webhook URL and secret from system parameters."""
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "url": ICP.get_param("ipai.webhook.url", ""),
            "secret": ICP.get_param("ipai.webhook.secret", ""),
        }

    def _compute_hmac_signature(self, payload_str, secret, timestamp):
        """Compute HMAC-SHA256 signature for webhook payload."""
        message = f"{timestamp}.{payload_str}"
        return hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _emit_integration_event(self, event_type, payload_extra=None):
        """Emit an event to the Supabase integration bus.

        Args:
            event_type: Event type (e.g., 'asset.reserved')
            payload_extra: Additional payload data to merge
        """
        config = self._get_integration_config()
        if not config["url"]:
            _logger.debug("Integration webhook URL not configured, skipping event")
            return

        for equipment in self:
            try:
                timestamp = str(int(time.time()))
                idempotency_key = (
                    f"asset-{equipment.id}-{event_type}-{timestamp[:10]}"
                )

                payload = {
                    "source": "odoo",
                    "event_type": event_type,
                    "aggregate_type": "asset_booking",
                    "aggregate_id": f"maintenance.equipment,{equipment.id}",
                    "idempotency_key": idempotency_key,
                    "payload": {
                        "equipment_id": equipment.id,
                        "name": equipment.name,
                        "serial_no": equipment.serial_no or "",
                        "category": equipment.category_id.name if equipment.category_id else "",
                        "asset_status": equipment.asset_status,
                        "assigned_employee_id": equipment.assigned_employee_id.id if equipment.assigned_employee_id else None,
                        "assigned_employee_name": equipment.assigned_employee_id.name if equipment.assigned_employee_id else "",
                        "checkout_date": str(equipment.checkout_date) if equipment.checkout_date else None,
                        "expected_return_date": str(equipment.expected_return_date) if equipment.expected_return_date else None,
                    },
                }

                if payload_extra:
                    payload["payload"].update(payload_extra)

                payload_str = json.dumps(payload, default=str)
                signature = self._compute_hmac_signature(
                    payload_str, config["secret"], timestamp
                )

                headers = {
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Timestamp": timestamp,
                }

                response = requests.post(
                    config["url"],
                    data=payload_str,
                    headers=headers,
                    timeout=10,
                )
                response.raise_for_status()

                equipment.sudo().write({
                    "integration_last_event": event_type,
                    "integration_last_event_at": fields.Datetime.now(),
                })
                _logger.info(
                    "Emitted integration event %s for equipment %s",
                    event_type,
                    equipment.id,
                )

            except requests.RequestException as e:
                _logger.error(
                    "Failed to emit integration event %s for equipment %s: %s",
                    event_type,
                    equipment.id,
                    str(e),
                )
            except Exception as e:
                _logger.exception(
                    "Unexpected error emitting event %s for equipment %s: %s",
                    event_type,
                    equipment.id,
                    str(e),
                )

    def action_reserve(self, employee_id):
        """Reserve equipment for an employee."""
        self.ensure_one()
        self.write({
            "asset_status": "reserved",
            "assigned_employee_id": employee_id,
        })
        self._emit_integration_event("asset.reserved")
        return True

    def action_checkout(self):
        """Check out equipment to assigned employee."""
        for equipment in self:
            if equipment.asset_status not in ("available", "reserved"):
                continue
            equipment.write({
                "asset_status": "checked_out",
                "checkout_date": fields.Date.today(),
            })
            equipment._emit_integration_event("asset.checked_out")
        return True

    def action_checkin(self):
        """Return equipment."""
        for equipment in self:
            if equipment.asset_status != "checked_out":
                continue
            equipment.write({
                "asset_status": "available",
                "assigned_employee_id": False,
                "checkout_date": False,
                "expected_return_date": False,
            })
            equipment._emit_integration_event("asset.checked_in")
        return True

    @api.model
    def _cron_check_overdue_assets(self):
        """Scheduled action to check for overdue assets."""
        today = fields.Date.today()
        overdue_equipment = self.search([
            ("asset_status", "=", "checked_out"),
            ("expected_return_date", "<", today),
        ])
        for equipment in overdue_equipment:
            equipment._emit_integration_event(
                "asset.overdue",
                payload_extra={
                    "days_overdue": (today - equipment.expected_return_date).days,
                },
            )
        return True
