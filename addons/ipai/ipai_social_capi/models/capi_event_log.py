"""CAPI event log — tracks all events sent to Meta for audit and replay."""

import json
import logging
import uuid

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class CapiEventLog(models.Model):
    _name = "ipai.capi.event.log"
    _description = "Meta CAPI Event Log"
    _order = "create_date desc"
    _rec_name = "event_id"

    # Event identity
    event_id = fields.Char(required=True, index=True, readonly=True)
    event_type = fields.Selection(
        [
            ("lead_created", "Lead Created"),
            ("lead_qualified", "Lead Qualified"),
            ("opportunity_won", "Opportunity Won"),
            ("invoice_paid", "Invoice Paid"),
        ],
        required=True,
        readonly=True,
    )

    # Source record
    res_model = fields.Char(readonly=True)
    res_id = fields.Integer(readonly=True)

    # Delivery status
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("sent", "Sent"),
            ("failed", "Failed"),
            ("dead_lettered", "Dead-Lettered"),
        ],
        default="pending",
        readonly=True,
        index=True,
    )
    events_received = fields.Integer(readonly=True)
    error_message = fields.Text(readonly=True)
    payload_json = fields.Text(readonly=True)
    correlation_id = fields.Char(readonly=True)

    @api.model
    def _get_bridge_url(self):
        """Get CAPI bridge Azure Function URL from system parameters."""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_social_capi.bridge_url", "")
        )

    @api.model
    def _get_bridge_key(self):
        """Get CAPI bridge function key from system parameters."""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_social_capi.bridge_function_key", "")
        )

    @api.model
    def _is_enabled(self):
        """Check if CAPI bridge is enabled."""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_social_capi.enabled", "False")
            == "True"
        )

    @api.model
    def send_event(self, event_type, record, user_data, custom_data=None):
        """Create log entry and relay event to CAPI bridge.

        Args:
            event_type: One of lead_created, lead_qualified, opportunity_won, invoice_paid.
            record: Source Odoo record (crm.lead, account.move).
            user_data: Dict with email, phone, first_name, last_name, etc.
            custom_data: Optional dict with value, currency, order_id, etc.

        Returns:
            Created ipai.capi.event.log record.
        """
        if not self._is_enabled():
            logger.debug("CAPI bridge disabled, skipping %s", event_type)
            return self.env["ipai.capi.event.log"]

        event_id = str(uuid.uuid4())
        correlation_id = str(uuid.uuid4())

        canonical_event = {
            "event_type": event_type,
            "event_id": event_id,
            "user": user_data,
            "source_url": self._build_source_url(record),
        }
        if custom_data:
            canonical_event["custom_data"] = custom_data

        log = self.sudo().create(
            {
                "event_id": event_id,
                "event_type": event_type,
                "res_model": record._name,
                "res_id": record.id,
                "correlation_id": correlation_id,
                "payload_json": json.dumps(
                    canonical_event, default=str, indent=2
                ),
                "state": "pending",
            }
        )

        self._relay_to_bridge(log, canonical_event, correlation_id)
        return log

    def _relay_to_bridge(self, log, canonical_event, correlation_id):
        """POST event to Azure Function CAPI bridge."""
        bridge_url = self._get_bridge_url()
        bridge_key = self._get_bridge_key()

        if not bridge_url:
            log.sudo().write(
                {
                    "state": "failed",
                    "error_message": "Bridge URL not configured (ipai_social_capi.bridge_url)",
                }
            )
            return

        headers = {
            "Content-Type": "application/json",
            "X-Correlation-ID": correlation_id,
        }
        if bridge_key:
            headers["x-functions-key"] = bridge_key

        payload = {"events": [canonical_event]}

        try:
            resp = requests.post(
                f"{bridge_url}/api/capi-relay",
                json=payload,
                headers=headers,
                timeout=30,
            )

            if resp.status_code == 200:
                result = resp.json()
                log.sudo().write(
                    {
                        "state": "sent",
                        "events_received": result.get("events_received", 0),
                    }
                )
                logger.info(
                    "CAPI event %s delivered: %s",
                    log.event_id,
                    result.get("events_received"),
                )
            elif resp.status_code == 502:
                result = resp.json()
                log.sudo().write(
                    {
                        "state": "dead_lettered",
                        "error_message": result.get("error", resp.text[:500]),
                    }
                )
                logger.warning(
                    "CAPI event %s dead-lettered: %s",
                    log.event_id,
                    result.get("error"),
                )
            else:
                log.sudo().write(
                    {
                        "state": "failed",
                        "error_message": f"HTTP {resp.status_code}: {resp.text[:500]}",
                    }
                )
                logger.error(
                    "CAPI event %s failed: HTTP %s",
                    log.event_id,
                    resp.status_code,
                )
        except requests.RequestException as e:
            log.sudo().write(
                {
                    "state": "failed",
                    "error_message": str(e)[:500],
                }
            )
            logger.error("CAPI event %s request error: %s", log.event_id, e)

    @api.model
    def _build_source_url(self, record):
        """Build Odoo URL for the source record."""
        base_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("web.base.url", "https://erp.insightpulseai.com")
        )
        if record._name == "crm.lead":
            return f"{base_url}/odoo/crm/{record.id}"
        if record._name == "account.move":
            return f"{base_url}/odoo/accounting/customer-invoices/{record.id}"
        return f"{base_url}/odoo/{record._name}/{record.id}"
