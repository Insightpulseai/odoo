# -*- coding: utf-8 -*-
"""
Control Room Run Models
========================

Execution tracking for pipelines:

1. control.run - Single pipeline execution instance
2. control.run.event - Timeline events/logs for a run

Architecture:
    Pipeline → Run → Events + Artifacts
"""

from odoo import api, fields, models


class ControlRun(models.Model):
    """
    Pipeline Run

    Represents a single execution instance of a pipeline.
    Tracks state, timing, context, and related artifacts/events.
    """

    _name = "control.run"
    _description = "Pipeline Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "started_at DESC, id DESC"

    # Identity
    name = fields.Char(
        string="Run Name",
        compute="_compute_name",
        store=True,
    )

    # Relationships
    pipeline_id = fields.Many2one(
        "control.pipeline",
        string="Pipeline",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
    )

    # Execution Details
    requested_by = fields.Many2one(
        "res.users",
        string="Requested By",
        default=lambda self: self.env.user,
    )
    trigger_source = fields.Selection(
        [
            ("manual", "Manual"),
            ("schedule", "Scheduled"),
            ("webhook", "Webhook"),
            ("event", "Event"),
            ("api", "API"),
        ],
        string="Trigger Source",
        default="manual",
    )

    # State
    state = fields.Selection(
        [
            ("queued", "Queued"),
            ("running", "Running"),
            ("succeeded", "Succeeded"),
            ("failed", "Failed"),
            ("canceled", "Canceled"),
        ],
        string="State",
        default="queued",
        required=True,
        tracking=True,
        index=True,
    )

    # Timing
    queued_at = fields.Datetime(
        string="Queued At",
        default=fields.Datetime.now,
    )
    started_at = fields.Datetime(
        string="Started At",
    )
    finished_at = fields.Datetime(
        string="Finished At",
    )
    duration_s = fields.Integer(
        string="Duration (seconds)",
        compute="_compute_duration",
        store=True,
    )

    # Context
    run_context_json = fields.Text(
        string="Run Context (JSON)",
        help="Resolved parameters, environment, actor context",
    )
    env_id = fields.Many2one(
        "control.env",
        string="Environment",
    )

    # Results
    result_json = fields.Text(
        string="Result (JSON)",
        help="Execution result data",
    )
    error_message = fields.Text(
        string="Error Message",
    )
    error_step_id = fields.Many2one(
        "control.pipeline.step",
        string="Failed Step",
    )

    # Related Records
    artifact_ids = fields.One2many(
        "control.artifact",
        "run_id",
        string="Artifacts",
    )
    event_ids = fields.One2many(
        "control.run.event",
        "run_id",
        string="Events",
    )
    artifact_count = fields.Integer(
        string="Artifact Count",
        compute="_compute_counts",
    )
    event_count = fields.Integer(
        string="Event Count",
        compute="_compute_counts",
    )

    # Step Progress
    current_stage = fields.Char(
        string="Current Stage",
    )
    current_step = fields.Char(
        string="Current Step",
    )
    progress_pct = fields.Float(
        string="Progress (%)",
        default=0.0,
    )

    @api.depends("pipeline_id.name", "queued_at")
    def _compute_name(self):
        for record in self:
            if record.pipeline_id and record.queued_at:
                ts = fields.Datetime.to_string(record.queued_at)[:16]
                record.name = f"{record.pipeline_id.name} @ {ts}"
            elif record.pipeline_id:
                record.name = f"{record.pipeline_id.name} (pending)"
            else:
                record.name = "New Run"

    @api.depends("started_at", "finished_at")
    def _compute_duration(self):
        for record in self:
            if record.started_at and record.finished_at:
                delta = record.finished_at - record.started_at
                record.duration_s = int(delta.total_seconds())
            else:
                record.duration_s = 0

    @api.depends("artifact_ids", "event_ids")
    def _compute_counts(self):
        for record in self:
            record.artifact_count = len(record.artifact_ids)
            record.event_count = len(record.event_ids)

    def action_start(self):
        """Mark run as started"""
        self.ensure_one()
        self.write(
            {
                "state": "running",
                "started_at": fields.Datetime.now(),
            }
        )
        self._log_event("info", "Run started")

    def action_complete(self):
        """Mark run as succeeded"""
        self.ensure_one()
        self.write(
            {
                "state": "succeeded",
                "finished_at": fields.Datetime.now(),
                "progress_pct": 100.0,
            }
        )
        self._log_event("info", "Run completed successfully")

    def action_fail(self, error_message=None):
        """Mark run as failed"""
        self.ensure_one()
        self.write(
            {
                "state": "failed",
                "finished_at": fields.Datetime.now(),
                "error_message": error_message,
            }
        )
        self._log_event("error", f"Run failed: {error_message or 'Unknown error'}")

    def action_cancel(self):
        """Cancel the run"""
        self.ensure_one()
        self.write(
            {
                "state": "canceled",
                "finished_at": fields.Datetime.now(),
            }
        )
        self._log_event("warn", "Run canceled by user")

    def action_retry(self):
        """Create a retry run from this failed run"""
        self.ensure_one()
        return self.pipeline_id.action_trigger_run()

    def _log_event(self, level, message, step_id=None, payload=None):
        """Helper to create a run event"""
        self.env["control.run.event"].create(
            {
                "run_id": self.id,
                "level": level,
                "message": message,
                "step_id": step_id,
                "payload_json": payload,
            }
        )


class ControlRunEvent(models.Model):
    """
    Run Event

    Timeline entry for run observability.
    Captures logs, state transitions, and metrics.
    """

    _name = "control.run.event"
    _description = "Run Event"
    _order = "ts DESC, id DESC"

    # Relationships
    run_id = fields.Many2one(
        "control.run",
        string="Run",
        required=True,
        ondelete="cascade",
        index=True,
    )
    step_id = fields.Many2one(
        "control.pipeline.step",
        string="Step",
        help="Associated step (if applicable)",
    )

    # Event Details
    ts = fields.Datetime(
        string="Timestamp",
        default=fields.Datetime.now,
        index=True,
    )
    level = fields.Selection(
        [
            ("debug", "Debug"),
            ("info", "Info"),
            ("warn", "Warning"),
            ("error", "Error"),
        ],
        string="Level",
        default="info",
        required=True,
    )
    message = fields.Text(
        string="Message",
        required=True,
    )

    # Payload
    payload_json = fields.Text(
        string="Payload (JSON)",
        help="Structured event data",
    )

    # External References
    external_ref = fields.Char(
        string="External Reference",
        help="Job ID, K8s pod name, etc.",
    )
    source = fields.Char(
        string="Source",
        help="Event source identifier",
    )
