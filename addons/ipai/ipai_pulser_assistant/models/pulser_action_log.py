# -*- coding: utf-8 -*-
"""
pulser.action.log — Audited action log.

Every Pulser action must emit: rationale, source inputs, confidence,
referenced policy/rule, reversible audit trace (Constitution Principle 6).
Log is append-only — no unlink for users (only manager + admin).
"""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PulserActionLog(models.Model):
    _name = "pulser.action.log"
    _description = "Pulser Action Log"
    _order = "timestamp desc"
    _rec_name = "action_description"

    timestamp = fields.Datetime(
        string="Timestamp",
        default=fields.Datetime.now,
        required=True,
        readonly=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
        ondelete="restrict",
    )
    agent_id = fields.Many2one(
        comodel_name="pulser.domain.agent",
        string="Domain Agent",
        ondelete="set null",
    )
    intent_type = fields.Selection(
        selection=[
            ("informational", "Informational"),
            ("navigational", "Navigational"),
            ("transactional", "Transactional"),
        ],
        string="Intent Type",
        required=True,
    )
    action_class = fields.Selection(
        selection=[
            ("advisory", "Advisory"),
            ("approval_gated", "Approval-Gated"),
            ("auto_routable", "Auto-Routable"),
        ],
        string="Action Class",
        required=True,
    )
    target_model = fields.Char(string="Target Model", readonly=True)
    target_record_id = fields.Integer(string="Target Record ID", readonly=True)
    action_description = fields.Text(
        string="Action Description",
        required=True,
        help="Human-readable description of what this action did or proposed",
    )
    rationale = fields.Text(
        string="Rationale",
        help="Why this action was selected (explainability — Principle 6)",
    )
    inputs_summary = fields.Text(
        string="Inputs Summary",
        help="Summary of data inputs that informed this action",
    )
    confidence = fields.Float(
        string="Confidence",
        digits=(5, 4),
        help="Model confidence score 0.0–1.0",
    )
    policy_reference = fields.Char(
        string="Policy Reference",
        help="Referenced policy or rule that governs this action",
    )
    outcome = fields.Selection(
        selection=[
            ("success", "Success"),
            ("failed", "Failed"),
            ("pending_approval", "Pending Approval"),
            ("rejected", "Rejected"),
        ],
        string="Outcome",
        required=True,
        default="pending_approval",
    )
    error_message = fields.Text(string="Error Message")
    duration_ms = fields.Integer(
        string="Duration (ms)",
        help="End-to-end action duration in milliseconds",
    )
    interaction_id = fields.Many2one(
        comodel_name="pulser.interaction",
        string="Interaction",
        ondelete="cascade",
        help="Parent interaction trace this action log belongs to",
    )

    @api.constrains("confidence")
    def _check_confidence_bounds(self):
        for rec in self:
            if rec.confidence is not False and not (0.0 <= rec.confidence <= 1.0):
                raise ValidationError(
                    f"Confidence must be between 0.0 and 1.0, got {rec.confidence}"
                )

    @api.constrains("action_class", "intent_type")
    def _check_transactional_class(self):
        """Enforce: transactional intents must have a classified action class."""
        for rec in self:
            if rec.intent_type == "transactional" and not rec.action_class:
                raise ValidationError(
                    "Transactional actions must have an action class. "
                    "No unclassified transactional action may be logged."
                )
