# -*- coding: utf-8 -*-
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiJob(models.Model):
    """Outbound job queue for external integrations.

    This model implements a simple queue/outbox pattern for:
    - AI analysis requests
    - Sync events to Supabase
    - Webhook callbacks
    """

    _name = "ipai.job"
    _description = "IPAI Integration Job"
    _order = "create_date desc"

    name = fields.Char(string="Job Name", required=True)
    job_type = fields.Selection(
        [
            ("ai_analysis", "AI Analysis"),
            ("sync_event", "Sync Event"),
            ("webhook", "Webhook Callback"),
            ("export", "Data Export"),
        ],
        string="Job Type",
        required=True,
    )
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
        default="pending",
        index=True,
    )
    model_name = fields.Char(string="Model Name")
    record_id = fields.Integer(string="Record ID")
    payload = fields.Text(string="Payload (JSON)")
    result = fields.Text(string="Result (JSON)")
    error_message = fields.Text(string="Error Message")
    retry_count = fields.Integer(string="Retry Count", default=0)
    max_retries = fields.Integer(string="Max Retries", default=3)
    scheduled_date = fields.Datetime(string="Scheduled Date")
    completed_date = fields.Datetime(string="Completed Date")

    @api.model
    def process_pending_jobs(self, limit=100):
        """Cron job to process pending jobs.

        This method is called by scheduled action to process
        pending jobs in the queue.
        """
        pending_jobs = self.search(
            [
                ("state", "=", "pending"),
                "|",
                ("scheduled_date", "=", False),
                ("scheduled_date", "<=", fields.Datetime.now()),
            ],
            limit=limit,
            order="create_date asc",
        )

        for job in pending_jobs:
            try:
                job._process_job()
            except Exception as e:
                _logger.exception(f"Error processing job {job.id}: {e}")
                job._mark_failed(str(e))

    def _process_job(self):
        """Process a single job. Override per job_type."""
        self.ensure_one()
        self.write({"state": "processing"})

        # Route to appropriate handler
        handler = getattr(self, f"_process_{self.job_type}", None)
        if handler:
            handler()
        else:
            _logger.warning(f"No handler for job type: {self.job_type}")
            self._mark_completed({})

    def _process_ai_analysis(self):
        """Process AI analysis job."""
        # Placeholder: would call external AI endpoint
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        endpoint = IrConfigParameter.get_param("ipai_bridge.ai_endpoint_url")

        if not endpoint:
            self._mark_failed("AI endpoint not configured")
            return

        # TODO: Implement actual HTTP call to AI endpoint
        # For now, mark as completed with placeholder
        self._mark_completed({"status": "placeholder", "endpoint": endpoint})

    def _process_sync_event(self):
        """Process sync event job."""
        # Placeholder: would push to Supabase
        self._mark_completed({"status": "placeholder"})

    def _process_webhook(self):
        """Process webhook callback job."""
        # Placeholder: would call webhook URL
        self._mark_completed({"status": "placeholder"})

    def _process_export(self):
        """Process data export job."""
        # Placeholder: would export data
        self._mark_completed({"status": "placeholder"})

    def _mark_completed(self, result):
        """Mark job as completed with result."""
        self.write(
            {
                "state": "completed",
                "result": json.dumps(result) if result else None,
                "completed_date": fields.Datetime.now(),
            }
        )

    def _mark_failed(self, error_message):
        """Mark job as failed or retry if retries remaining."""
        self.ensure_one()
        if self.retry_count < self.max_retries:
            self.write(
                {
                    "state": "pending",
                    "retry_count": self.retry_count + 1,
                    "error_message": error_message,
                }
            )
        else:
            self.write(
                {
                    "state": "failed",
                    "error_message": error_message,
                }
            )
