# -*- coding: utf-8 -*-
from odoo import api, fields, models


class N8nExecution(models.Model):
    """n8n workflow execution log."""

    _name = "ipai.n8n.execution"
    _description = "n8n Workflow Execution"
    _order = "create_date desc"

    workflow_id = fields.Many2one(
        "ipai.n8n.workflow",
        required=True,
        ondelete="cascade"
    )
    connector_id = fields.Many2one(
        related="workflow_id.connector_id",
        store=True
    )

    # n8n execution ID
    n8n_execution_id = fields.Char(index=True)

    # Execution details
    trigger_source = fields.Selection([
        ("webhook", "Webhook"),
        ("schedule", "Schedule"),
        ("manual", "Manual (n8n UI)"),
        ("odoo_manual", "Manual (Odoo)"),
        ("odoo_webhook", "Odoo Webhook"),
    ])

    status = fields.Selection([
        ("waiting", "Waiting"),
        ("running", "Running"),
        ("success", "Success"),
        ("error", "Error"),
        ("canceled", "Canceled"),
    ], default="waiting")

    # Timing
    started_at = fields.Datetime()
    finished_at = fields.Datetime()
    duration_ms = fields.Integer(compute="_compute_duration")

    # Data
    input_data = fields.Text(help="Input data (JSON)")
    output_data = fields.Text(help="Output data (JSON)")
    error_message = fields.Text()

    # Related Odoo records
    res_model = fields.Char(help="Related Odoo model")
    res_id = fields.Integer(help="Related Odoo record ID")

    def _compute_duration(self):
        for rec in self:
            if rec.started_at and rec.finished_at:
                delta = rec.finished_at - rec.started_at
                rec.duration_ms = int(delta.total_seconds() * 1000)
            else:
                rec.duration_ms = 0

    @api.model
    def log_webhook_trigger(self, workflow, payload, result=None, error=None):
        """Log a webhook-triggered execution."""
        return self.create({
            "workflow_id": workflow.id,
            "trigger_source": "odoo_webhook",
            "status": "success" if result else "error",
            "input_data": str(payload),
            "output_data": str(result) if result else None,
            "error_message": error,
            "started_at": fields.Datetime.now(),
            "finished_at": fields.Datetime.now(),
        })
