# -*- coding: utf-8 -*-
"""
pulser.interaction — Full interaction trace record.

Every Pulser shell session produces an interaction trace: intent, routing,
tools invoked, result, latency, and user feedback (PRD FR-6).
Sessions are keyed by session_id (client-generated UUID or similar).
"""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PulserInteraction(models.Model):
    _name = "pulser.interaction"
    _description = "Pulser Interaction Trace"
    _order = "timestamp desc"
    _rec_name = "session_id"

    session_id = fields.Char(
        string="Session ID",
        required=True,
        index=True,
        help="Client-generated session identifier (UUID or similar)",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        default=lambda self: self.env.user,
        ondelete="restrict",
    )
    timestamp = fields.Datetime(
        string="Timestamp",
        default=fields.Datetime.now,
        required=True,
        readonly=True,
    )
    query = fields.Text(
        string="User Query",
        required=True,
        help="Raw user input to the copilot shell",
    )
    response = fields.Text(
        string="Assistant Response",
        help="Final response delivered to the user",
    )
    intent_type = fields.Selection(
        selection=[
            ("informational", "Informational"),
            ("navigational", "Navigational"),
            ("transactional", "Transactional"),
        ],
        string="Detected Intent",
    )
    agent_id = fields.Many2one(
        comodel_name="pulser.domain.agent",
        string="Routed Agent",
        ondelete="set null",
        help="Domain agent that handled this interaction (if any)",
    )
    action_log_ids = fields.One2many(
        comodel_name="pulser.action.log",
        inverse_name="interaction_id",
        string="Action Logs",
    )
    feedback = fields.Selection(
        selection=[
            ("positive", "Positive"),
            ("negative", "Negative"),
            ("none", "No Feedback"),
        ],
        string="User Feedback",
        default="none",
    )
    duration_ms = fields.Integer(
        string="Total Duration (ms)",
        help="Wall-clock time from query receipt to response delivery",
    )
    tools_invoked = fields.Char(
        string="Tools Invoked",
        help="Comma-separated list of tool names invoked during this interaction",
    )

    @api.constrains("session_id")
    def _check_session_id(self):
        for rec in self:
            if not rec.session_id or not rec.session_id.strip():
                raise ValidationError("Session ID cannot be blank.")
