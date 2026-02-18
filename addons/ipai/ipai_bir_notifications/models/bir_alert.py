"""BIR Alert Model - Email notifications for tax filing deadlines."""

import logging
from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.tools import format_datetime

_logger = logging.getLogger(__name__)


class BIRAlert(models.Model):
    """BIR Alert - Track notification history and prevent spam."""

    _name = "bir.alert"
    _description = "BIR Tax Filing Alert"
    _order = "create_date desc"

    filing_deadline_id = fields.Many2one(
        "bir.filing.deadline",
        string="Filing Deadline",
        required=True,
        ondelete="cascade",
        index=True,
    )
    alert_type = fields.Selection(
        [
            ("digest", "Daily Digest"),
            ("urgent", "Urgent Alert"),
        ],
        string="Alert Type",
        required=True,
        default="digest",
    )
    recipient_email = fields.Char(
        string="Recipient Email",
        required=True,
    )
    sent_date = fields.Datetime(
        string="Sent Date",
        default=fields.Datetime.now,
        required=True,
    )
    subject = fields.Char(string="Email Subject")
    body_text = fields.Text(string="Email Body (Plain Text)")
    status = fields.Selection(
        [
            ("sent", "Sent"),
            ("failed", "Failed"),
        ],
        string="Status",
        default="sent",
        required=True,
    )
    error_message = fields.Text(string="Error Message")

    @api.model
    def send_daily_digest(self):
        """
        Cron job: Send daily digest (08:00 PH time).

        Summarizes:
        - Upcoming deadlines (next 7 days)
        - Overdue filings
        - Today's deadlines

        Returns:
            bool: True if digest sent successfully
        """
        _logger.info("Starting BIR daily digest job (08:00 PH)")

        # Get recipients from system parameters or company settings
        recipients = self._get_digest_recipients()
        if not recipients:
            _logger.warning("No digest recipients configured - skipping daily digest")
            return False

        # Gather deadline data
        today = fields.Date.today()
        seven_days = today + timedelta(days=7)

        # Upcoming deadlines (next 7 days)
        upcoming = self.env["bir.filing.deadline"].search([
            ("deadline_date", ">=", today),
            ("deadline_date", "<=", seven_days),
            ("status", "in", ["pending", "in_progress"]),
        ], order="deadline_date asc")

        # Overdue filings
        overdue = self.env["bir.filing.deadline"].search([
            ("deadline_date", "<", today),
            ("status", "in", ["pending", "in_progress"]),
        ], order="deadline_date asc")

        # Today's deadlines
        today_deadlines = self.env["bir.filing.deadline"].search([
            ("deadline_date", "=", today),
            ("status", "in", ["pending", "in_progress"]),
        ])

        # Skip if nothing to report
        if not upcoming and not overdue and not today_deadlines:
            _logger.info("No deadlines to report - skipping daily digest")
            return True

        # Generate email content
        subject = self._format_digest_subject(today, len(overdue), len(today_deadlines))
        body_text = self._format_digest_body(today, upcoming, overdue, today_deadlines)

        # Send to all recipients
        success = True
        for recipient in recipients:
            try:
                self._send_email(
                    recipient=recipient,
                    subject=subject,
                    body_text=body_text,
                    alert_type="digest",
                    deadline_ids=upcoming.ids + overdue.ids + today_deadlines.ids,
                )
                _logger.info(f"Daily digest sent to {recipient}")
            except Exception as e:
                _logger.error(f"Failed to send digest to {recipient}: {e}")
                success = False

        return success

    @api.model
    def send_urgent_alert(self, deadline_id):
        """
        Send urgent alert for deadline <24h or critical issue.

        Args:
            deadline_id: int - ID of bir.filing.deadline record

        Returns:
            bool: True if alert sent successfully
        """
        deadline = self.env["bir.filing.deadline"].browse(deadline_id)
        if not deadline.exists():
            _logger.error(f"Deadline {deadline_id} not found")
            return False

        # Check if already alerted recently (prevent spam)
        last_alert_time = self._get_last_alert_time(deadline_id, "urgent")
        if last_alert_time:
            hours_since = (datetime.now() - last_alert_time).total_seconds() / 3600
            if hours_since < 4:  # Don't re-alert within 4 hours
                _logger.info(f"Skipping urgent alert for {deadline.form_type} - alerted {hours_since:.1f}h ago")
                return True

        # Get recipients
        recipients = self._get_urgent_recipients()
        if not recipients:
            _logger.warning("No urgent alert recipients configured")
            return False

        # Calculate hours until deadline
        now = datetime.now()
        deadline_dt = datetime.combine(deadline.deadline_date, datetime.min.time())
        hours_remaining = (deadline_dt - now).total_seconds() / 3600

        # Generate email content
        subject = self._format_urgent_subject(deadline, hours_remaining)
        body_text = self._format_urgent_body(deadline, hours_remaining)

        # Send to all recipients
        success = True
        for recipient in recipients:
            try:
                self._send_email(
                    recipient=recipient,
                    subject=subject,
                    body_text=body_text,
                    alert_type="urgent",
                    deadline_ids=[deadline_id],
                )
                _logger.info(f"Urgent alert sent to {recipient} for {deadline.form_type}")
            except Exception as e:
                _logger.error(f"Failed to send urgent alert to {recipient}: {e}")
                success = False

        return success

    @api.model
    def check_urgent_deadlines(self):
        """
        Cron job: Check for urgent deadlines (<24h) every 4 hours.

        Returns:
            bool: True if check completed successfully
        """
        _logger.info("Checking for urgent BIR deadlines (<24h)")

        tomorrow = fields.Date.today() + timedelta(days=1)

        # Find deadlines within 24 hours
        urgent_deadlines = self.env["bir.filing.deadline"].search([
            ("deadline_date", "<=", tomorrow),
            ("deadline_date", ">=", fields.Date.today()),
            ("status", "in", ["pending", "in_progress"]),
        ])

        if not urgent_deadlines:
            _logger.info("No urgent deadlines found")
            return True

        _logger.info(f"Found {len(urgent_deadlines)} urgent deadlines")

        # Send alert for each
        for deadline in urgent_deadlines:
            self.send_urgent_alert(deadline.id)

        return True

    def _send_email(self, recipient, subject, body_text, alert_type, deadline_ids):
        """
        Send email via Zoho Mail SMTP.

        Args:
            recipient: str - Email address
            subject: str - Email subject
            body_text: str - Plain text email body
            alert_type: str - "digest" or "urgent"
            deadline_ids: list - List of deadline IDs for tracking
        """
        # Get mail server (configured in Odoo settings)
        mail_server = self.env["ir.mail_server"].sudo().search([
            ("smtp_host", "=", "smtp.zoho.com"),
        ], limit=1)

        if not mail_server:
            raise ValueError("Zoho Mail SMTP not configured in Odoo")

        # Create mail message
        mail_values = {
            "subject": subject,
            "body_html": f"<pre>{body_text}</pre>",  # Plain text in <pre> for simplicity
            "email_from": mail_server.smtp_user,
            "email_to": recipient,
            "mail_server_id": mail_server.id,
        }

        mail = self.env["mail.mail"].sudo().create(mail_values)

        try:
            mail.send()

            # Record alert history (one record per deadline)
            for deadline_id in deadline_ids:
                self.create({
                    "filing_deadline_id": deadline_id,
                    "alert_type": alert_type,
                    "recipient_email": recipient,
                    "subject": subject,
                    "body_text": body_text,
                    "status": "sent",
                })

        except Exception as e:
            _logger.error(f"Email send failed: {e}")

            # Record failure
            for deadline_id in deadline_ids:
                self.create({
                    "filing_deadline_id": deadline_id,
                    "alert_type": alert_type,
                    "recipient_email": recipient,
                    "subject": subject,
                    "body_text": body_text,
                    "status": "failed",
                    "error_message": str(e),
                })

            raise

    def _get_digest_recipients(self):
        """Get list of email addresses for daily digest."""
        # Option 1: System parameter
        param = self.env["ir.config_parameter"].sudo().get_param(
            "ipai_bir_notifications.digest_recipients"
        )
        if param:
            return [email.strip() for email in param.split(",")]

        # Option 2: Company settings (fallback)
        company = self.env.company
        if company.email:
            return [company.email]

        return []

    def _get_urgent_recipients(self):
        """Get list of email addresses for urgent alerts."""
        # Option 1: System parameter
        param = self.env["ir.config_parameter"].sudo().get_param(
            "ipai_bir_notifications.urgent_recipients"
        )
        if param:
            return [email.strip() for email in param.split(",")]

        # Option 2: Same as digest recipients (fallback)
        return self._get_digest_recipients()

    def _get_last_alert_time(self, deadline_id, alert_type):
        """Get timestamp of last alert for this deadline."""
        last_alert = self.search([
            ("filing_deadline_id", "=", deadline_id),
            ("alert_type", "=", alert_type),
            ("status", "=", "sent"),
        ], order="sent_date desc", limit=1)

        if last_alert:
            return last_alert.sent_date
        return None

    def _format_digest_subject(self, today, overdue_count, today_count):
        """Format daily digest subject line."""
        parts = ["BIR Tax Filing Digest"]

        if today_count > 0:
            parts.append(f"{today_count} due today")

        if overdue_count > 0:
            parts.append(f"{overdue_count} overdue")

        parts.append(f"- {today.strftime('%Y-%m-%d')}")

        return " | ".join(parts)

    def _format_digest_body(self, today, upcoming, overdue, today_deadlines):
        """Format daily digest email body (plain text)."""
        lines = []
        lines.append("=" * 70)
        lines.append("BIR TAX FILING DIGEST")
        lines.append(f"Date: {today.strftime('%A, %B %d, %Y')}")
        lines.append("=" * 70)
        lines.append("")

        # Today's deadlines
        if today_deadlines:
            lines.append("📅 DUE TODAY:")
            lines.append("-" * 70)
            for dl in today_deadlines:
                lines.append(f"  • {dl.form_type} - {dl.description or 'No description'}")
                lines.append(f"    Period: {dl.period_start} to {dl.period_end}")
                lines.append(f"    Status: {dl.status.upper()}")
                lines.append("")

        # Overdue filings
        if overdue:
            lines.append("⚠️  OVERDUE FILINGS:")
            lines.append("-" * 70)
            for dl in overdue:
                days_late = (today - dl.deadline_date).days
                lines.append(f"  • {dl.form_type} - {days_late} days late")
                lines.append(f"    Deadline: {dl.deadline_date}")
                lines.append(f"    Period: {dl.period_start} to {dl.period_end}")
                lines.append(f"    Status: {dl.status.upper()}")
                lines.append("")

        # Upcoming (next 7 days)
        if upcoming:
            lines.append("📋 UPCOMING (Next 7 Days):")
            lines.append("-" * 70)
            for dl in upcoming:
                days_remaining = (dl.deadline_date - today).days
                lines.append(f"  • {dl.form_type} - {days_remaining} days remaining")
                lines.append(f"    Deadline: {dl.deadline_date.strftime('%Y-%m-%d (%A)')}")
                lines.append(f"    Period: {dl.period_start} to {dl.period_end}")
                lines.append(f"    Status: {dl.status.upper()}")
                lines.append("")

        lines.append("=" * 70)
        lines.append("This is an automated daily digest from InsightPulseAI Odoo ERP.")
        lines.append("To update recipients, contact your system administrator.")
        lines.append("=" * 70)

        return "\n".join(lines)

    def _format_urgent_subject(self, deadline, hours_remaining):
        """Format urgent alert subject line."""
        if hours_remaining < 0:
            return f"🚨 URGENT: {deadline.form_type} is OVERDUE"
        elif hours_remaining < 24:
            return f"🚨 URGENT: {deadline.form_type} due in {int(hours_remaining)}h"
        else:
            return f"⚠️  Alert: {deadline.form_type} approaching deadline"

    def _format_urgent_body(self, deadline, hours_remaining):
        """Format urgent alert email body (plain text)."""
        lines = []
        lines.append("=" * 70)
        lines.append("🚨 URGENT: BIR TAX FILING DEADLINE ALERT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Form Type: {deadline.form_type}")
        lines.append(f"Description: {deadline.description or 'N/A'}")
        lines.append(f"Filing Period: {deadline.period_start} to {deadline.period_end}")
        lines.append(f"Deadline: {deadline.deadline_date.strftime('%Y-%m-%d (%A)')}")
        lines.append("")

        if hours_remaining < 0:
            lines.append(f"STATUS: OVERDUE by {abs(int(hours_remaining))} hours")
        elif hours_remaining < 24:
            lines.append(f"TIME REMAINING: {int(hours_remaining)} hours")

        lines.append("")
        lines.append(f"Current Status: {deadline.status.upper()}")
        lines.append("")
        lines.append("=" * 70)
        lines.append("ACTION REQUIRED:")
        lines.append("  1. Review filing status in Odoo ERP")
        lines.append("  2. Complete and submit form before deadline")
        lines.append("  3. Update status in system once filed")
        lines.append("=" * 70)
        lines.append("")
        lines.append("This is an automated urgent alert from InsightPulseAI Odoo ERP.")
        lines.append("You will not receive another alert for this deadline for 4 hours.")
        lines.append("=" * 70)

        return "\n".join(lines)
