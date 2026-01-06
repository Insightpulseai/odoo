# -*- coding: utf-8 -*-
"""
Control Room Pipeline Models
=============================

Core models for pipeline definition and execution:

1. control.pipeline - Pipeline definition with metadata
2. control.pipeline.stage - Execution stages within a pipeline
3. control.pipeline.step - Individual steps within stages

Architecture:
    Pipeline → Stages → Steps → Runs → Events
"""

from odoo import api, fields, models


class ControlPipeline(models.Model):
    """
    Control Room Pipeline Definition

    Represents an automation workflow that can be triggered
    manually, on schedule, via webhook, or by events.
    """

    _name = "control.pipeline"
    _description = "Control Room Pipeline"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    # Identity
    name = fields.Char(
        string="Pipeline Name",
        required=True,
        tracking=True,
        help="Human-readable pipeline name",
    )
    code = fields.Char(
        string="Code",
        index=True,
        help="Unique identifier for API/automation use",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )

    # Ownership
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        help="Optional link to project for cross-functional coordination",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
        tracking=True,
    )

    # Description
    description = fields.Text(
        string="Description",
        help="Pipeline purpose and behavior documentation",
    )

    # Trigger Configuration
    trigger_type = fields.Selection(
        [
            ("manual", "Manual"),
            ("schedule", "Schedule"),
            ("webhook", "Webhook"),
            ("event", "Event"),
        ],
        string="Trigger Type",
        default="manual",
        required=True,
        tracking=True,
    )
    schedule_id = fields.Many2one(
        "control.schedule",
        string="Schedule",
        help="Cron schedule for scheduled pipelines",
    )
    webhook_secret = fields.Char(
        string="Webhook Secret",
        help="HMAC secret for webhook authentication (reference only)",
    )
    event_filter = fields.Char(
        string="Event Filter",
        help="Event type pattern for event-triggered pipelines",
    )

    # Environment
    default_env_id = fields.Many2one(
        "control.env",
        string="Default Environment",
        help="Default execution environment",
    )

    # Structure
    stage_ids = fields.One2many(
        "control.pipeline.stage",
        "pipeline_id",
        string="Stages",
    )
    stage_count = fields.Integer(
        string="Stage Count",
        compute="_compute_stage_count",
    )
    step_count = fields.Integer(
        string="Step Count",
        compute="_compute_step_count",
    )

    # Last Run Status
    last_run_id = fields.Many2one(
        "control.run",
        string="Last Run",
        readonly=True,
    )
    last_run_state = fields.Selection(
        related="last_run_id.state",
        string="Last Run State",
        store=True,
    )
    last_run_at = fields.Datetime(
        related="last_run_id.started_at",
        string="Last Run At",
        store=True,
    )

    # Statistics
    run_count = fields.Integer(
        string="Run Count",
        compute="_compute_run_stats",
    )
    success_rate = fields.Float(
        string="Success Rate (%)",
        compute="_compute_run_stats",
    )

    _sql_constraints = [
        (
            "code_company_uniq",
            "UNIQUE(code, company_id)",
            "Pipeline code must be unique per company",
        )
    ]

    @api.depends("stage_ids")
    def _compute_stage_count(self):
        for record in self:
            record.stage_count = len(record.stage_ids)

    @api.depends("stage_ids.step_ids")
    def _compute_step_count(self):
        for record in self:
            record.step_count = sum(len(stage.step_ids) for stage in record.stage_ids)

    def _compute_run_stats(self):
        Run = self.env["control.run"]
        for record in self:
            runs = Run.search([("pipeline_id", "=", record.id)])
            record.run_count = len(runs)
            if runs:
                succeeded = len(runs.filtered(lambda r: r.state == "succeeded"))
                record.success_rate = (succeeded / len(runs)) * 100
            else:
                record.success_rate = 0.0

    def action_trigger_run(self):
        """Create a new run for this pipeline"""
        self.ensure_one()
        Run = self.env["control.run"]
        run = Run.create({
            "pipeline_id": self.id,
            "company_id": self.company_id.id,
            "project_id": self.project_id.id if self.project_id else False,
            "requested_by": self.env.user.id,
            "state": "queued",
        })
        self.last_run_id = run.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "control.run",
            "res_id": run.id,
            "view_mode": "form",
            "target": "current",
        }


class ControlPipelineStage(models.Model):
    """
    Pipeline Stage

    Groups related steps within a pipeline for
    logical organization and execution flow.
    """

    _name = "control.pipeline.stage"
    _description = "Pipeline Stage"
    _order = "sequence, id"

    pipeline_id = fields.Many2one(
        "control.pipeline",
        string="Pipeline",
        required=True,
        ondelete="cascade",
        index=True,
    )
    name = fields.Char(
        string="Stage Name",
        required=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    description = fields.Text(
        string="Description",
    )

    # Steps
    step_ids = fields.One2many(
        "control.pipeline.step",
        "stage_id",
        string="Steps",
    )
    step_count = fields.Integer(
        string="Step Count",
        compute="_compute_step_count",
    )

    @api.depends("step_ids")
    def _compute_step_count(self):
        for record in self:
            record.step_count = len(record.step_ids)


class ControlPipelineStep(models.Model):
    """
    Pipeline Step

    Individual executable unit within a stage.
    Supports various step kinds (SQL, Python, HTTP, etc.)
    """

    _name = "control.pipeline.step"
    _description = "Pipeline Step"
    _order = "sequence, id"

    # Relationships
    stage_id = fields.Many2one(
        "control.pipeline.stage",
        string="Stage",
        required=True,
        ondelete="cascade",
        index=True,
    )
    pipeline_id = fields.Many2one(
        related="stage_id.pipeline_id",
        string="Pipeline",
        store=True,
        index=True,
    )

    # Identity
    name = fields.Char(
        string="Step Name",
        required=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    enabled = fields.Boolean(
        string="Enabled",
        default=True,
    )

    # Step Type
    kind = fields.Selection(
        [
            ("sql", "SQL Query"),
            ("python", "Python Script"),
            ("http", "HTTP Request"),
            ("connector", "Connector Call"),
            ("agent", "AI Agent"),
            ("shell", "Shell Command"),
            ("transform", "Data Transform"),
            ("odoo_action", "Odoo Action"),
        ],
        string="Step Kind",
        required=True,
        default="sql",
    )

    # Connector
    connector_id = fields.Many2one(
        "control.connector",
        string="Connector",
        help="External system connector for this step",
    )

    # Configuration (JSON)
    input_spec_json = fields.Text(
        string="Input Schema (JSON)",
        help="JSON Schema defining expected inputs",
    )
    output_spec_json = fields.Text(
        string="Output Schema (JSON)",
        help="JSON Schema defining expected outputs",
    )
    params_json = fields.Text(
        string="Parameters (JSON)",
        help="Step-specific configuration parameters",
    )
    retry_policy_json = fields.Text(
        string="Retry Policy (JSON)",
        default='{"max_attempts": 3, "backoff": "exponential"}',
        help="Retry configuration for failed steps",
    )

    # Execution Settings
    timeout_s = fields.Integer(
        string="Timeout (seconds)",
        default=300,
        help="Maximum execution time before timeout",
    )
    continue_on_error = fields.Boolean(
        string="Continue on Error",
        default=False,
        help="Continue pipeline execution if this step fails",
    )

    # Documentation
    description = fields.Text(
        string="Description",
    )


class ControlEnv(models.Model):
    """
    Execution Environment

    Defines runtime environment for pipeline execution
    (e.g., dev, staging, production).
    """

    _name = "control.env"
    _description = "Execution Environment"
    _order = "sequence, name"

    name = fields.Char(
        string="Environment Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
        index=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    description = fields.Text(
        string="Description",
    )
    color = fields.Integer(
        string="Color",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # Configuration
    config_json = fields.Text(
        string="Configuration (JSON)",
        help="Environment-specific configuration overrides",
    )

    _sql_constraints = [
        ("code_uniq", "UNIQUE(code)", "Environment code must be unique"),
    ]
