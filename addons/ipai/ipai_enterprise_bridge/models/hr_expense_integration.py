# -*- coding: utf-8 -*-
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""
HR Expense Integration - Event Emission for Supabase Integration Bus

Emits events when expense lifecycle changes occur:
- expense.submitted: Expense submitted for approval
- expense.approved: Expense approved
- expense.rejected: Expense rejected
- expense.paid: Expense paid/posted
"""
import hashlib
import hmac
import json
import logging
import time

import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HrExpenseIntegration(models.Model):
    """Extend hr.expense with integration event emission."""

    _inherit = "hr.expense"

    integration_last_event = fields.Char(
        string="Last Integration Event",
        readonly=True,
        copy=False,
        help="Last event emitted to the integration bus",
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
            event_type: Event type (e.g., 'expense.submitted')
            payload_extra: Additional payload data to merge
        """
        config = self._get_integration_config()
        if not config["url"]:
            _logger.debug("Integration webhook URL not configured, skipping event")
            return

        for expense in self:
            try:
                timestamp = str(int(time.time()))
                idempotency_key = f"expense-{expense.id}-{event_type}-{timestamp[:10]}"

                payload = {
                    "source": "odoo",
                    "event_type": event_type,
                    "aggregate_type": "expense",
                    "aggregate_id": f"hr.expense,{expense.id}",
                    "idempotency_key": idempotency_key,
                    "payload": {
                        "expense_id": expense.id,
                        "name": expense.name,
                        "employee_id": expense.employee_id.id,
                        "employee_name": expense.employee_id.name,
                        "total_amount": expense.total_amount,
                        "currency": expense.currency_id.name,
                        "state": expense.state,
                        "description": expense.description or "",
                        "date": str(expense.date) if expense.date else None,
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

                expense.sudo().write({
                    "integration_last_event": event_type,
                    "integration_last_event_at": fields.Datetime.now(),
                })
                _logger.info(
                    "Emitted integration event %s for expense %s",
                    event_type,
                    expense.id,
                )

            except requests.RequestException as e:
                _logger.error(
                    "Failed to emit integration event %s for expense %s: %s",
                    event_type,
                    expense.id,
                    str(e),
                )
            except Exception as e:
                _logger.exception(
                    "Unexpected error emitting event %s for expense %s: %s",
                    event_type,
                    expense.id,
                    str(e),
                )

    def action_submit_expenses(self):
        """Override to emit expense.submitted event."""
        result = super().action_submit_expenses()
        self._emit_integration_event("expense.submitted")
        return result

    def approve_expense_sheets(self):
        """Override to emit expense.approved event."""
        result = super().approve_expense_sheets()
        self._emit_integration_event("expense.approved")
        return result

    def refuse_expense_sheets(self, reason=None):
        """Override to emit expense.rejected event."""
        result = super().refuse_expense_sheets(reason=reason)
        self._emit_integration_event(
            "expense.rejected",
            payload_extra={"rejection_reason": reason or ""},
        )
        return result

    def action_sheet_move_post(self):
        """Override to emit expense.paid event when posted."""
        result = super().action_sheet_move_post()
        self._emit_integration_event("expense.paid")
        return result
