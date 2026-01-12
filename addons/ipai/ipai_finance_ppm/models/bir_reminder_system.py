# -*- coding: utf-8 -*-
"""BIR Deadline Reminder System

Automated reminders for BIR filing deadlines:
- 9AM & 5PM reminders on due date
- Daily nudges when overdue until completed
"""

import json
import logging
from datetime import date, timedelta

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class BirFormSchedule(models.Model):
    _inherit = "ipai.bir.form.schedule"

    # Add fields for reminder tracking
    last_reminder_sent = fields.Datetime(string="Last Reminder Sent", readonly=True)
    reminder_count = fields.Integer(string="Reminder Count", default=0, readonly=True)
    status = fields.Selection(
        [
            ("not_started", "Not Started"),
            ("in_progress", "In Progress"),
            ("submitted", "Submitted"),
            ("filed", "Filed"),
            ("late", "Late"),
        ],
        string="Status",
        default="not_started",
        tracking=True,
    )
    filing_date = fields.Date(string="Filing Date", tracking=True)

    @api.model
    def action_send_due_date_9am_reminder(self):
        """Send 9AM reminder for BIR forms due today"""
        forms_due_today = self.search(
            [
                ("bir_deadline", "=", fields.Date.today()),
                ("status", "not in", ["filed", "submitted"]),
            ]
        )

        webhook_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "bir.reminder.n8n.webhook",
                "https://ipa.insightpulseai.net/webhook/bir-reminder",
            )
        )

        for form in forms_due_today:
            self._send_reminder_webhook(form, "due_date_9am", webhook_url)
            form.write(
                {
                    "last_reminder_sent": fields.Datetime.now(),
                    "reminder_count": form.reminder_count + 1,
                }
            )

        _logger.info(
            f"Sent 9AM reminders for {len(forms_due_today)} BIR forms due today"
        )
        return True

    @api.model
    def action_send_due_date_5pm_reminder(self):
        """Send 5PM reminder for BIR forms due today"""
        forms_due_today = self.search(
            [
                ("bir_deadline", "=", fields.Date.today()),
                ("status", "not in", ["filed", "submitted"]),
            ]
        )

        webhook_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "bir.reminder.n8n.webhook",
                "https://ipa.insightpulseai.net/webhook/bir-reminder",
            )
        )

        for form in forms_due_today:
            self._send_reminder_webhook(form, "due_date_5pm", webhook_url)
            form.write(
                {
                    "last_reminder_sent": fields.Datetime.now(),
                    "reminder_count": form.reminder_count + 1,
                }
            )

        _logger.info(
            f"Sent 5PM reminders for {len(forms_due_today)} BIR forms due today"
        )
        return True

    @api.model
    def action_send_overdue_daily_nudge(self):
        """Send daily nudge for overdue BIR forms"""
        overdue_forms = self.search(
            [
                ("bir_deadline", "<", fields.Date.today()),
                ("status", "not in", ["filed", "submitted"]),
            ]
        )

        webhook_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "bir.overdue.n8n.webhook",
                "https://ipa.insightpulseai.net/webhook/bir-overdue-nudge",
            )
        )

        for form in overdue_forms:
            days_overdue = (fields.Date.today() - form.bir_deadline).days
            penalty_risk = self._calculate_penalty_risk(days_overdue)

            self._send_overdue_webhook(form, days_overdue, penalty_risk, webhook_url)
            form.write(
                {
                    "last_reminder_sent": fields.Datetime.now(),
                    "reminder_count": form.reminder_count + 1,
                    "status": "late",
                }
            )

        _logger.info(f"Sent daily nudges for {len(overdue_forms)} overdue BIR forms")
        return True

    def _send_reminder_webhook(self, form, reminder_type, webhook_url):
        """Send reminder to n8n webhook"""
        # Get responsible person email
        if form.responsible_prep_id:
            responsible_email = form.responsible_prep_id.email or "finance-team@omc.com"
        else:
            responsible_email = "finance-team@omc.com"

        payload = {
            "reminder_type": reminder_type,
            "bir_form": form.form_code,
            "period": form.period,
            "deadline": form.bir_deadline.isoformat() if form.bir_deadline else None,
            "responsible_email": responsible_email,
            "status": form.status,
            "form_id": form.id,
        }

        try:
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            _logger.info(
                f"Reminder sent for {form.form_code} ({form.period}): {reminder_type}"
            )
        except Exception as e:
            _logger.error(f"Failed to send reminder for {form.form_code}: {str(e)}")

    def _send_overdue_webhook(self, form, days_overdue, penalty_risk, webhook_url):
        """Send overdue nudge to n8n webhook"""
        # Get responsible person email
        if form.responsible_prep_id:
            responsible_email = form.responsible_prep_id.email or "finance-team@omc.com"
        else:
            responsible_email = "finance-team@omc.com"

        payload = {
            "reminder_type": "overdue_daily",
            "bir_form": form.form_code,
            "period": form.period,
            "deadline": form.bir_deadline.isoformat() if form.bir_deadline else None,
            "days_overdue": days_overdue,
            "penalty_risk": penalty_risk,
            "responsible_email": responsible_email,
            "status": form.status,
            "form_id": form.id,
        }

        try:
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            _logger.info(
                f"Overdue nudge sent for {form.form_code}: {days_overdue} days overdue"
            )
        except Exception as e:
            _logger.error(
                f"Failed to send overdue nudge for {form.form_code}: {str(e)}"
            )

    def _calculate_penalty_risk(self, days_overdue):
        """Calculate penalty risk based on days overdue"""
        if days_overdue >= 30:
            return "CRITICAL"
        elif days_overdue >= 7:
            return "HIGH"
        else:
            return "MEDIUM"

    @api.model
    def send_mattermost_direct(self, message_text):
        """Direct Mattermost send (fallback if n8n is unavailable)"""
        webhook_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("bir.reminder.mattermost.webhook")
        )

        if not webhook_url or "REPLACE_WITH_ACTUAL_WEBHOOK_ID" in webhook_url:
            _logger.warning("Mattermost webhook URL not configured")
            return False

        payload = {
            "text": message_text,
            "username": "BIR Reminder Bot",
            "icon_emoji": ":calendar:",
        }

        try:
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            return True
        except Exception as e:
            _logger.error(f"Failed to send Mattermost message: {str(e)}")
            return False
