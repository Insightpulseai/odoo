# -*- coding: utf-8 -*-
import logging

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PlatformDeployment(models.Model):
    """Deployment records"""

    _name = "platform.deployment"
    _description = "Platform Deployment"
    _order = "create_date desc"

    name = fields.Char(string="Deployment", compute="_compute_name", store=True)
    branch = fields.Char(string="Branch", required=True)
    environment = fields.Selection(
        [
            ("production", "Production"),
            ("staging", "Staging"),
            ("development", "Development"),
        ],
        string="Environment",
        required=True,
    )
    status = fields.Selection(
        [
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        string="Status",
        default="pending",
        required=True,
    )

    # Git info
    commit_hash = fields.Char(string="Commit Hash")
    commit_message = fields.Text(string="Commit Message")
    commit_author = fields.Char(string="Author")

    # Timestamps
    started_at = fields.Datetime(string="Started At")
    completed_at = fields.Datetime(string="Completed At")
    duration = fields.Integer(
        string="Duration (seconds)", compute="_compute_duration", store=True
    )

    # Logs
    build_log = fields.Text(string="Build Log")
    error_message = fields.Text(string="Error Message")

    # n8n integration
    n8n_execution_id = fields.Char(string="n8n Execution ID")
    n8n_webhook_url = fields.Char(
        string="n8n Webhook URL",
        default=lambda self: self.env["ir.config_parameter"]
        .sudo()
        .get_param("n8n.webhook_url"),
    )

    @api.depends("branch", "environment")
    def _compute_name(self):
        for record in self:
            record.name = f"{record.environment}/{record.branch}"

    @api.depends("started_at", "completed_at")
    def _compute_duration(self):
        for record in self:
            if record.started_at and record.completed_at:
                delta = record.completed_at - record.started_at
                record.duration = int(delta.total_seconds())
            else:
                record.duration = 0

    def action_trigger_deployment(self):
        """Trigger deployment via n8n webhook"""
        self.ensure_one()

        if not self.n8n_webhook_url:
            raise UserWarning("n8n webhook URL not configured")

        # Update status
        self.write(
            {
                "status": "in_progress",
                "started_at": fields.Datetime.now(),
            }
        )

        # Call n8n webhook
        try:
            response = requests.post(
                self.n8n_webhook_url,
                json={
                    "deployment_id": self.id,
                    "branch": self.branch,
                    "environment": self.environment,
                    "commit_hash": self.commit_hash,
                },
                timeout=10,
            )
            response.raise_for_status()

            result = response.json()
            self.n8n_execution_id = result.get("execution_id")

            _logger.info(f"Triggered deployment {self.id} via n8n")

        except Exception as e:
            _logger.error(f"Failed to trigger deployment: {str(e)}")
            self.write(
                {
                    "status": "failed",
                    "error_message": str(e),
                    "completed_at": fields.Datetime.now(),
                }
            )
            raise

        return True

    def action_mark_success(self):
        """Mark deployment as successful"""
        self.write(
            {
                "status": "success",
                "completed_at": fields.Datetime.now(),
            }
        )

    def action_mark_failed(self, error_message=None):
        """Mark deployment as failed"""
        self.write(
            {
                "status": "failed",
                "error_message": error_message,
                "completed_at": fields.Datetime.now(),
            }
        )

    @api.model
    def get_recent_deployments(self, limit=10):
        """Return recent deployments for API"""
        deployments = self.search([], limit=limit)
        return [
            {
                "id": d.id,
                "branch": d.branch,
                "environment": d.environment,
                "status": d.status,
                "commit_hash": d.commit_hash,
                "commit_message": d.commit_message,
                "started_at": d.started_at.isoformat() if d.started_at else None,
                "completed_at": d.completed_at.isoformat() if d.completed_at else None,
                "duration": d.duration,
            }
            for d in deployments
        ]
