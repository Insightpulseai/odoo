# -*- coding: utf-8 -*-
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""
Project Task Integration - Event Emission for Supabase Integration Bus

Emits events when finance/project task lifecycle changes occur:
- finance_task.created: Task created
- finance_task.in_progress: Task started
- finance_task.submitted: Task submitted for review
- finance_task.approved: Task approved
- finance_task.filed: Task filed/completed
- finance_task.overdue: Task overdue
"""
import hashlib
import hmac
import json
import logging
import time

import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProjectTaskIntegration(models.Model):
    """Extend project.task with integration event emission for finance tasks."""

    _inherit = "project.task"

    # Finance task fields
    is_finance_task = fields.Boolean(
        string="Finance Task",
        default=False,
        help="Mark as finance/compliance task for integration tracking",
    )
    finance_task_type = fields.Selection(
        [
            ("bir_filing", "BIR Filing"),
            ("vat_return", "VAT Return"),
            ("withholding_tax", "Withholding Tax"),
            ("month_end", "Month End Close"),
            ("audit", "Audit"),
            ("reconciliation", "Reconciliation"),
            ("other", "Other"),
        ],
        string="Finance Task Type",
    )
    filing_deadline = fields.Date(string="Filing Deadline")
    filing_reference = fields.Char(string="Filing Reference")

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
            event_type: Event type (e.g., 'finance_task.created')
            payload_extra: Additional payload data to merge
        """
        config = self._get_integration_config()
        if not config["url"]:
            _logger.debug("Integration webhook URL not configured, skipping event")
            return

        for task in self:
            if not task.is_finance_task:
                continue

            try:
                timestamp = str(int(time.time()))
                idempotency_key = (
                    f"finance_task-{task.id}-{event_type}-{timestamp[:10]}"
                )

                payload = {
                    "source": "odoo",
                    "event_type": event_type,
                    "aggregate_type": "finance_task",
                    "aggregate_id": f"project.task,{task.id}",
                    "idempotency_key": idempotency_key,
                    "payload": {
                        "task_id": task.id,
                        "name": task.name,
                        "project_id": task.project_id.id if task.project_id else None,
                        "project_name": task.project_id.name if task.project_id else "",
                        "user_id": task.user_ids[0].id if task.user_ids else None,
                        "user_name": task.user_ids[0].name if task.user_ids else "",
                        "stage_id": task.stage_id.id if task.stage_id else None,
                        "stage_name": task.stage_id.name if task.stage_id else "",
                        "finance_task_type": task.finance_task_type or "",
                        "filing_deadline": str(task.filing_deadline) if task.filing_deadline else None,
                        "filing_reference": task.filing_reference or "",
                        "date_deadline": str(task.date_deadline) if task.date_deadline else None,
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

                task.sudo().write({
                    "integration_last_event": event_type,
                    "integration_last_event_at": fields.Datetime.now(),
                })
                _logger.info(
                    "Emitted integration event %s for finance task %s",
                    event_type,
                    task.id,
                )

            except requests.RequestException as e:
                _logger.error(
                    "Failed to emit integration event %s for task %s: %s",
                    event_type,
                    task.id,
                    str(e),
                )
            except Exception as e:
                _logger.exception(
                    "Unexpected error emitting event %s for task %s: %s",
                    event_type,
                    task.id,
                    str(e),
                )

    @api.model_create_multi
    def create(self, vals_list):
        """Override to emit finance_task.created event."""
        tasks = super().create(vals_list)
        finance_tasks = tasks.filtered(lambda t: t.is_finance_task)
        finance_tasks._emit_integration_event("finance_task.created")
        return tasks

    def write(self, vals):
        """Override to emit events on stage changes for finance tasks."""
        # Detect stage changes
        stage_changed = "stage_id" in vals
        old_stages = {task.id: task.stage_id.name for task in self} if stage_changed else {}

        result = super().write(vals)

        if stage_changed:
            for task in self.filtered(lambda t: t.is_finance_task):
                new_stage = task.stage_id.name.lower() if task.stage_id else ""

                # Map stage names to events
                if "progress" in new_stage or "doing" in new_stage:
                    task._emit_integration_event("finance_task.in_progress")
                elif "review" in new_stage or "submit" in new_stage:
                    task._emit_integration_event("finance_task.submitted")
                elif "approved" in new_stage or "done" in new_stage:
                    task._emit_integration_event("finance_task.approved")
                elif "filed" in new_stage or "complete" in new_stage:
                    task._emit_integration_event("finance_task.filed")

        return result

    @api.model
    def _cron_check_overdue_finance_tasks(self):
        """Scheduled action to check for overdue finance tasks."""
        today = fields.Date.today()
        overdue_tasks = self.search([
            ("is_finance_task", "=", True),
            ("filing_deadline", "<", today),
            ("stage_id.fold", "=", False),  # Not in a "done" stage
        ])
        for task in overdue_tasks:
            task._emit_integration_event(
                "finance_task.overdue",
                payload_extra={
                    "days_overdue": (today - task.filing_deadline).days,
                },
            )
        return True
