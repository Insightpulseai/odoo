# -*- coding: utf-8 -*-
"""
Control Room Playbook Model
============================

Standard response procedures for common scenarios.
"""

from odoo import api, fields, models


class ControlPlaybook(models.Model):
    """
    Control Playbook

    Defines a standard response procedure with steps
    and optional automation hooks.
    """

    _name = "control.playbook"
    _description = "Control Playbook"
    _order = "category, name"

    # Identity
    name = fields.Char(
        string="Playbook Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        index=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # Category
    category = fields.Selection(
        [
            ("incident", "Incident Response"),
            ("dq_fix", "Data Quality Fix"),
            ("cost_opt", "Cost Optimization"),
            ("perf_opt", "Performance Optimization"),
            ("security", "Security Response"),
            ("compliance", "Compliance Check"),
            ("onboarding", "Onboarding"),
            ("offboarding", "Offboarding"),
            ("maintenance", "Maintenance"),
            ("custom", "Custom"),
        ],
        string="Category",
        required=True,
        default="custom",
    )

    # Trigger
    trigger_type = fields.Selection(
        [
            ("manual", "Manual Only"),
            ("advice", "On Advice Accept"),
            ("dq_fail", "On DQ Check Fail"),
            ("run_fail", "On Pipeline Fail"),
            ("webhook", "Webhook"),
        ],
        string="Trigger Type",
        default="manual",
    )

    # Steps
    steps_json = fields.Text(
        string="Steps (JSON)",
        help="Ordered list of playbook steps",
        default="[]",
    )
    step_count = fields.Integer(
        string="Step Count",
        compute="_compute_step_count",
    )

    # Automation
    automation_hook = fields.Selection(
        [
            ("none", "None"),
            ("pipeline", "Trigger Pipeline"),
            ("n8n", "Trigger n8n Workflow"),
            ("webhook", "Call Webhook"),
            ("odoo_action", "Run Odoo Action"),
        ],
        string="Automation Hook",
        default="none",
    )
    automation_pipeline_id = fields.Many2one(
        "control.pipeline",
        string="Automation Pipeline",
    )
    automation_config_json = fields.Text(
        string="Automation Config (JSON)",
    )

    # Ownership
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    # Documentation
    description = fields.Text(
        string="Description",
    )
    documentation_url = fields.Char(
        string="Documentation URL",
    )

    # Statistics
    execution_count = fields.Integer(
        string="Execution Count",
        compute="_compute_execution_count",
    )
    last_executed_at = fields.Datetime(
        string="Last Executed At",
    )

    # Related
    action_ids = fields.One2many(
        "control.action",
        "playbook_id",
        string="Actions",
    )
    advice_ids = fields.One2many(
        "control.advice",
        "playbook_id",
        string="Suggested For Advice",
    )

    _sql_constraints = [
        (
            "code_company_uniq",
            "UNIQUE(code, company_id)",
            "Playbook code must be unique per company",
        )
    ]

    @api.depends("steps_json")
    def _compute_step_count(self):
        import json

        for record in self:
            if record.steps_json:
                try:
                    steps = json.loads(record.steps_json)
                    record.step_count = len(steps) if isinstance(steps, list) else 0
                except (json.JSONDecodeError, TypeError):
                    record.step_count = 0
            else:
                record.step_count = 0

    @api.depends("action_ids")
    def _compute_execution_count(self):
        for record in self:
            record.execution_count = len(record.action_ids)

    def action_execute(self):
        """Create an action to execute this playbook"""
        self.ensure_one()
        Action = self.env["control.action"]
        action = Action.create(
            {
                "playbook_id": self.id,
                "action_type": "playbook_run",
                "state": "pending",
            }
        )
        self.last_executed_at = fields.Datetime.now()
        return {
            "type": "ir.actions.act_window",
            "res_model": "control.action",
            "res_id": action.id,
            "view_mode": "form",
            "target": "current",
        }
