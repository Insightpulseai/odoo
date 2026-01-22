# -*- coding: utf-8 -*-
"""
HR Expense Integration - IPAI Event Emission
Emit events to Supabase integration bus for expense lifecycle
"""

from datetime import timedelta
from odoo import models, api
from odoo.addons.ipai_enterprise_bridge.utils.ipai_webhook import send_ipai_event
import logging

_logger = logging.getLogger(__name__)


class HrExpenseIntegration(models.Model):
    _inherit = 'hr.expense'

    def action_submit_expenses(self):
        """Override: Emit expense.submitted event when expense is submitted"""
        res = super().action_submit_expenses()

        # Get webhook config
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            _logger.warning("IPAI webhook not configured - skipping event emission")
            return res

        # Emit event for each expense
        for expense in self:
            event = {
                "event_type": "expense.submitted",
                "aggregate_type": "expense",
                "aggregate_id": str(expense.id),
                "payload": {
                    "expense_id": expense.id,
                    "employee_id": expense.employee_id.id if expense.employee_id else None,
                    "employee_name": expense.employee_id.name if expense.employee_id else None,
                    "employee_code": expense.employee_id.employee_code if expense.employee_id and hasattr(expense.employee_id, 'employee_code') else None,
                    "amount": float(expense.total_amount),
                    "currency": expense.currency_id.name if expense.currency_id else None,
                    "description": expense.name or "",
                    "date": expense.date.isoformat() if expense.date else None,
                    "category": expense.product_id.name if expense.product_id else None,
                    "submitted_at": expense.write_date.isoformat() if expense.write_date else None,
                    "state": expense.state,
                }
            }

            # Use composite key for idempotency
            idempotency_key = f"expense.submitted:{expense.id}:{expense.write_date.timestamp()}"

            try:
                send_ipai_event(webhook_url, webhook_secret, event, idempotency_key=idempotency_key)
                _logger.info(f"✅ Emitted expense.submitted event for expense #{expense.id}")
            except Exception as e:
                _logger.error(f"❌ Failed to emit expense.submitted event: {e}")

        return res

    def approve_expense_sheets(self):
        """Override: Emit expense.approved event when expense is approved"""
        res = super().approve_expense_sheets()

        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            return res

        for expense in self:
            event = {
                "event_type": "expense.approved",
                "aggregate_type": "expense",
                "aggregate_id": str(expense.id),
                "payload": {
                    "expense_id": expense.id,
                    "employee_id": expense.employee_id.id if expense.employee_id else None,
                    "employee_name": expense.employee_id.name if expense.employee_id else None,
                    "amount": float(expense.total_amount),
                    "currency": expense.currency_id.name if expense.currency_id else None,
                    "approved_by": self.env.user.name,
                    "approved_at": expense.write_date.isoformat() if expense.write_date else None,
                    "state": expense.state,
                }
            }

            idempotency_key = f"expense.approved:{expense.id}:{expense.write_date.timestamp()}"

            try:
                send_ipai_event(webhook_url, webhook_secret, event, idempotency_key=idempotency_key)
                _logger.info(f"✅ Emitted expense.approved event for expense #{expense.id}")
            except Exception as e:
                _logger.error(f"❌ Failed to emit expense.approved event: {e}")

        return res

    def refuse_expense(self, reason):
        """Override: Emit expense.rejected event when expense is rejected"""
        res = super().refuse_expense(reason)

        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            return res

        for expense in self:
            event = {
                "event_type": "expense.rejected",
                "aggregate_type": "expense",
                "aggregate_id": str(expense.id),
                "payload": {
                    "expense_id": expense.id,
                    "employee_id": expense.employee_id.id if expense.employee_id else None,
                    "employee_name": expense.employee_id.name if expense.employee_id else None,
                    "amount": float(expense.total_amount),
                    "currency": expense.currency_id.name if expense.currency_id else None,
                    "rejection_reason": reason,
                    "rejected_by": self.env.user.name,
                    "rejected_at": expense.write_date.isoformat() if expense.write_date else None,
                    "state": expense.state,
                }
            }

            idempotency_key = f"expense.rejected:{expense.id}:{expense.write_date.timestamp()}"

            try:
                send_ipai_event(webhook_url, webhook_secret, event, idempotency_key=idempotency_key)
                _logger.info(f"✅ Emitted expense.rejected event for expense #{expense.id}")
            except Exception as e:
                _logger.error(f"❌ Failed to emit expense.rejected event: {e}")

        return res

    @api.model
    def _cron_detect_paid_expenses(self):
        """
        Cron job to detect when expenses are paid (journal entry posted)
        Emits expense.paid event

        Run this cron daily to check for newly paid expenses
        """
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            return

        # Find expenses that were recently marked as 'done' (paid)
        # This assumes 'done' state means payment journal entry was posted
        recent_paid = self.search([
            ('state', '=', 'done'),
            ('write_date', '>=', (self.env.cr.now() - timedelta(days=1)).isoformat())
        ])

        for expense in recent_paid:
            event = {
                "event_type": "expense.paid",
                "aggregate_type": "expense",
                "aggregate_id": str(expense.id),
                "payload": {
                    "expense_id": expense.id,
                    "employee_id": expense.employee_id.id if expense.employee_id else None,
                    "employee_name": expense.employee_id.name if expense.employee_id else None,
                    "amount": float(expense.total_amount),
                    "currency": expense.currency_id.name if expense.currency_id else None,
                    "payment_date": expense.write_date.isoformat() if expense.write_date else None,
                    "state": expense.state,
                }
            }

            idempotency_key = f"expense.paid:{expense.id}:{expense.write_date.timestamp()}"

            try:
                send_ipai_event(webhook_url, webhook_secret, event, idempotency_key=idempotency_key)
                _logger.info(f"✅ Emitted expense.paid event for expense #{expense.id}")
            except Exception as e:
                _logger.error(f"❌ Failed to emit expense.paid event: {e}")
