# -*- coding: utf-8 -*-
"""
Finance PPM Task Integration - IPAI Event Emission
Emit events to Supabase integration bus for finance task lifecycle.

Uses Odoo-native fields (date_deadline, project_id, tag_ids) for
filtering and payload construction. No dependency on external models.
"""

from datetime import timedelta
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.ipai_enterprise_bridge.utils.ipai_webhook import send_ipai_event
except ImportError:
    send_ipai_event = None
    _logger.info("ipai_enterprise_bridge not installed — event emission disabled")


class ProjectTaskIntegration(models.Model):
    _inherit = 'project.task'

    def _is_finance_ppm_task(self):
        """Check if task belongs to a Finance PPM project (by project name convention)."""
        if not self.project_id:
            return False
        return 'Finance PPM' in (self.project_id.name or '')

    @api.model_create_multi
    def create(self, vals_list):
        """Override: Emit finance_task.created for Finance PPM tasks"""
        tasks = super().create(vals_list)

        for task in tasks.filtered(lambda t: t._is_finance_ppm_task()):
            self._emit_finance_task_event(task, 'finance_task.created')

        return tasks

    def write(self, vals):
        """Override: Emit events when task state changes"""
        res = super().write(vals)

        if 'stage_id' in vals:
            for task in self:
                if task._is_finance_ppm_task():
                    event_type = self._get_event_type_for_stage(task)
                    if event_type:
                        self._emit_finance_task_event(task, event_type)

        return res

    def _get_event_type_for_stage(self, task):
        """Map task stage to event type"""
        if not task.stage_id:
            return None

        stage_name = task.stage_id.name.lower()

        # Month-End stages: Preparation → Review → Approval
        # BIR stages: Preparation → Report Approval → Payment Approval → Filing & Payment
        if 'preparation' in stage_name:
            return 'finance_task.in_progress'
        elif 'review' in stage_name:
            return 'finance_task.submitted'
        elif 'report approval' in stage_name:
            return 'finance_task.submitted'
        elif 'payment approval' in stage_name:
            return 'finance_task.payment_approved'
        elif 'approval' in stage_name:
            return 'finance_task.approved'
        elif 'filing' in stage_name:
            return 'finance_task.filed'
        elif 'done' in stage_name:
            return 'finance_task.approved'

        return None

    def _emit_finance_task_event(self, task, event_type):
        """Emit finance task event to integration bus"""
        if send_ipai_event is None:
            return

        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            _logger.warning("IPAI webhook not configured — skipping event emission")
            return

        # Build payload using Odoo-native fields only
        tag_names = task.tag_ids.mapped('name') if task.tag_ids else []
        payload = {
            "task_id": task.id,
            "task_name": task.name,
            "project_name": task.project_id.name if task.project_id else "",
            "status": task.stage_id.name if task.stage_id else None,
            "new_stage": task.stage_id.name if task.stage_id else None,
            "assigned_to": task.user_ids[0].name if task.user_ids else None,
            "date_deadline": task.date_deadline.isoformat() if task.date_deadline else None,
            "tags": tag_names,
            "milestone": task.milestone_id.name if task.milestone_id else None,
            "assignee_emails": [u.email for u in task.user_ids if u.email],
            "write_date_unix": int(task.write_date.timestamp()) if task.write_date else 0,
        }

        event = {
            "event_type": event_type,
            "aggregate_type": "finance_task",
            "aggregate_id": str(task.id),
            "payload": payload,
        }

        idempotency_key = f"{event_type}:{task.id}:{task.write_date.timestamp()}"

        try:
            send_ipai_event(webhook_url, webhook_secret, event, idempotency_key=idempotency_key)
            _logger.info("Emitted %s event for task #%s", event_type, task.id)
        except Exception as e:
            _logger.error("Failed to emit %s event: %s", event_type, e)

    @api.model
    def _cron_detect_overdue_finance_tasks(self):
        """
        Cron job to detect overdue finance tasks.
        Uses Odoo-native date_deadline field on project.task.
        Run daily to check for deadline breaches.
        """
        if send_ipai_event is None:
            return

        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            return

        # Find tasks past their deadline and not yet completed
        # Uses Odoo-native date_deadline field
        done_stage_ids = self.env['project.task.type'].search([
            ('name', 'in', ['Done', 'Cancelled', 'Filing & Payment']),
        ]).ids

        overdue_tasks = self.search([
            ('date_deadline', '<', fields.Date.today()),
            ('date_deadline', '!=', False),
            ('stage_id', 'not in', done_stage_ids),
            ('project_id.name', 'ilike', 'Finance PPM'),
        ])

        for task in overdue_tasks:
            days_overdue = (fields.Date.today() - task.date_deadline).days if task.date_deadline else 0
            event = {
                "event_type": "finance_task.overdue",
                "aggregate_type": "finance_task",
                "aggregate_id": str(task.id),
                "payload": {
                    "task_id": task.id,
                    "task_name": task.name,
                    "project_name": task.project_id.name if task.project_id else "",
                    "date_deadline": task.date_deadline.isoformat() if task.date_deadline else None,
                    "days_overdue": days_overdue,
                    "assigned_to": task.user_ids[0].name if task.user_ids else None,
                    "status": task.stage_id.name if task.stage_id else None,
                    "tags": task.tag_ids.mapped('name') if task.tag_ids else [],
                },
            }

            idempotency_key = f"finance_task.overdue:{task.id}:{fields.Date.today().isoformat()}"

            try:
                send_ipai_event(webhook_url, webhook_secret, event, idempotency_key=idempotency_key)
                _logger.info("Emitted finance_task.overdue event for task #%s", task.id)
            except Exception as e:
                _logger.error("Failed to emit finance_task.overdue event: %s", e)

        _logger.info("Overdue finance task detection completed — %d overdue tasks found", len(overdue_tasks))
