# -*- coding: utf-8 -*-
"""
Control Room Advice Model
==========================

AI-generated recommendations and insights.
"""

from odoo import api, fields, models


class ControlAdvice(models.Model):
    """
    Control Advice

    Represents an AI-generated or system recommendation
    for improving operations, cost, performance, etc.
    """

    _name = "control.advice"
    _description = "Control Room Advice"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date DESC"

    # Identity
    name = fields.Char(
        string="Title",
        compute="_compute_name",
        store=True,
    )
    title = fields.Char(
        string="Advice Title",
        required=True,
    )

    # Ownership
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=True,
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
    )

    # Category
    category = fields.Selection(
        [
            ("cost", "Cost Optimization"),
            ("perf", "Performance"),
            ("security", "Security"),
            ("reliability", "Reliability"),
            ("data_quality", "Data Quality"),
            ("ux", "User Experience"),
            ("compliance", "Compliance"),
            ("process", "Process Improvement"),
        ],
        string="Category",
        required=True,
        index=True,
    )

    # Details
    summary = fields.Text(
        string="Summary",
        required=True,
    )
    impact = fields.Selection(
        [
            ("low", "Low Impact"),
            ("medium", "Medium Impact"),
            ("high", "High Impact"),
            ("critical", "Critical Impact"),
        ],
        string="Impact",
        default="medium",
    )
    confidence = fields.Float(
        string="Confidence (%)",
        help="AI confidence score for this recommendation",
        default=80.0,
    )
    effort = fields.Selection(
        [
            ("trivial", "Trivial (< 1 hour)"),
            ("low", "Low (< 1 day)"),
            ("medium", "Medium (< 1 week)"),
            ("high", "High (> 1 week)"),
        ],
        string="Effort",
        default="medium",
    )

    # Evidence
    evidence_json = fields.Text(
        string="Evidence (JSON)",
        help="Links to metrics, runs, DQ issues supporting this advice",
    )
    source = fields.Selection(
        [
            ("ai", "AI Generated"),
            ("rule", "Rule-Based"),
            ("manual", "Manual Entry"),
            ("integration", "External Integration"),
        ],
        string="Source",
        default="ai",
    )
    source_ref = fields.Char(
        string="Source Reference",
        help="Reference to the generating system/rule",
    )

    # Recommended Actions
    recommended_actions_json = fields.Text(
        string="Recommended Actions (JSON)",
        help="List of recommended actions to address this advice",
    )
    playbook_id = fields.Many2one(
        "control.playbook",
        string="Suggested Playbook",
    )

    # State
    state = fields.Selection(
        [
            ("new", "New"),
            ("accepted", "Accepted"),
            ("in_progress", "In Progress"),
            ("dismissed", "Dismissed"),
            ("done", "Done"),
        ],
        string="State",
        default="new",
        required=True,
        tracking=True,
        index=True,
    )
    dismissed_reason = fields.Text(
        string="Dismissal Reason",
    )

    # Related
    action_ids = fields.One2many(
        "control.action",
        "advice_id",
        string="Actions",
    )
    action_count = fields.Integer(
        string="Action Count",
        compute="_compute_action_count",
    )

    # Timing
    expires_at = fields.Datetime(
        string="Expires At",
        help="Advice validity expiration",
    )

    @api.depends("title")
    def _compute_name(self):
        for record in self:
            record.name = record.title or "New Advice"

    @api.depends("action_ids")
    def _compute_action_count(self):
        for record in self:
            record.action_count = len(record.action_ids)

    def action_accept(self):
        """Accept the advice"""
        self.write({"state": "accepted"})

    def action_dismiss(self):
        """Dismiss the advice"""
        self.write({"state": "dismissed"})

    def action_start(self):
        """Start working on the advice"""
        self.write({"state": "in_progress"})

    def action_complete(self):
        """Mark advice as done"""
        self.write({"state": "done"})

    def action_execute_playbook(self):
        """Execute the suggested playbook"""
        self.ensure_one()
        if not self.playbook_id:
            return False

        Action = self.env["control.action"]
        action = Action.create(
            {
                "advice_id": self.id,
                "playbook_id": self.playbook_id.id,
                "action_type": "playbook_run",
                "state": "pending",
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "control.action",
            "res_id": action.id,
            "view_mode": "form",
            "target": "current",
        }
