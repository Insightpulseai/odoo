# -*- coding: utf-8 -*-
"""
Finance PPM Task Integration - IPAI Event Emission
Emit events to Supabase integration bus for finance task lifecycle
"""

from datetime import timedelta
from odoo import models, fields, api
from odoo.addons.ipai_enterprise_bridge.utils.ipai_webhook import send_ipai_event
import logging

_logger = logging.getLogger(__name__)


class ProjectTaskIntegration(models.Model):
    _inherit = 'project.task'

    @api.model
    def create(self, vals):
        """Override: Emit finance_task.created when BIR task is auto-created"""
        task = super().create(vals)

        # Only emit for finance PPM tasks (linked to BIR schedule or logframe)
        if task.bir_schedule_id or task.finance_logframe_id:
            self._emit_finance_task_event(task, 'finance_task.created')

        return task

    def write(self, vals):
        """Override: Emit events when task state changes"""
        res = super().write(vals)

        # Detect state changes
        if 'stage_id' in vals or 'bir_schedule_id' in vals:
            for task in self:
                if task.bir_schedule_id or task.finance_logframe_id:
                    # Determine event type based on stage
                    event_type = self._get_event_type_for_stage(task)
                    if event_type:
                        self._emit_finance_task_event(task, event_type)

        return res

    def _get_event_type_for_stage(self, task):
        """Map task stage to event type"""
        if not task.stage_id:
            return None

        stage_name = task.stage_id.name.lower()

        # Map stage names to event types (customize based on your workflow)
        if 'progress' in stage_name or 'doing' in stage_name:
            return 'finance_task.in_progress'
        elif 'review' in stage_name or 'submitted' in stage_name:
            return 'finance_task.submitted'
        elif 'done' in stage_name or 'approved' in stage_name:
            return 'finance_task.approved'
        elif 'filed' in stage_name:
            return 'finance_task.filed'

        return None

    def _emit_finance_task_event(self, task, event_type):
        """Emit finance task event to integration bus"""
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            _logger.warning("IPAI webhook not configured - skipping event emission")
            return

        # Build payload
        payload = {
            "task_id": task.id,
            "task_name": task.name,
            "task_code": task.bir_schedule_id.task_code if task.bir_schedule_id else None,
            "bir_form": task.bir_schedule_id.bir_form if task.bir_schedule_id else None,
            "period_covered": task.bir_schedule_id.period_covered if task.bir_schedule_id else None,
            "employee_code": task.bir_schedule_id.employee_code if task.bir_schedule_id else None,
            "prep_deadline": task.bir_schedule_id.prep_deadline.isoformat() if task.bir_schedule_id and task.bir_schedule_id.prep_deadline else None,
            "filing_deadline": task.bir_schedule_id.filing_deadline.isoformat() if task.bir_schedule_id and task.bir_schedule_id.filing_deadline else None,
            "status": task.stage_id.name if task.stage_id else None,
            "assigned_to": task.user_ids[0].name if task.user_ids else None,
            "logframe_id": task.finance_logframe_id.id if task.finance_logframe_id else None,
            "logframe_level": task.finance_logframe_id.level if task.finance_logframe_id else None,
        }

        event = {
            "event_type": event_type,
            "aggregate_type": "finance_task",
            "aggregate_id": str(task.id),
            "payload": payload,
        }

        # Use composite key for idempotency
        idempotency_key = f"{event_type}:{task.id}:{task.write_date.timestamp()}"

        try:
            send_ipai_event(webhook_url, webhook_secret, event, idempotency_key=idempotency_key)
            _logger.info(f"✅ Emitted {event_type} event for task #{task.id}")
        except Exception as e:
            _logger.error(f"❌ Failed to emit {event_type} event: {e}")

    @api.model
    def _cron_detect_overdue_finance_tasks(self):
        """
        Cron job to detect overdue finance tasks
        Emits finance_task.overdue event

        Run this cron daily to check for deadline breaches
        """
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            return

        # Find tasks past their deadline and not yet completed
        overdue_tasks = self.search([
            ('bir_schedule_id', '!=', False),
            ('bir_schedule_id.filing_deadline', '<', fields.Date.today()),
            ('stage_id.name', 'not in', ['Done', 'Filed', 'Cancelled']),
        ])

        for task in overdue_tasks:
            event = {
                "event_type": "finance_task.overdue",
                "aggregate_type": "finance_task",
                "aggregate_id": str(task.id),
                "payload": {
                    "task_id": task.id,
                    "task_name": task.name,
                    "task_code": task.bir_schedule_id.task_code if task.bir_schedule_id else None,
                    "bir_form": task.bir_schedule_id.bir_form if task.bir_schedule_id else None,
                    "filing_deadline": task.bir_schedule_id.filing_deadline.isoformat() if task.bir_schedule_id and task.bir_schedule_id.filing_deadline else None,
                    "days_overdue": (fields.Date.today() - task.bir_schedule_id.filing_deadline).days if task.bir_schedule_id and task.bir_schedule_id.filing_deadline else 0,
                    "assigned_to": task.user_ids[0].name if task.user_ids else None,
                    "status": task.stage_id.name if task.stage_id else None,
                },
            }

            idempotency_key = f"finance_task.overdue:{task.id}:{fields.Date.today().isoformat()}"

            try:
                send_ipai_event(webhook_url, webhook_secret, event, idempotency_key=idempotency_key)
                _logger.info(f"✅ Emitted finance_task.overdue event for task #{task.id}")
            except Exception as e:
                _logger.error(f"❌ Failed to emit finance_task.overdue event: {e}")

        _logger.info(f"Overdue finance task detection completed - {len(overdue_tasks)} overdue tasks found")
