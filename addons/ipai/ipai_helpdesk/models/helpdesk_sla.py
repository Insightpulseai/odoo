# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing.

from odoo import models, fields, api


class HelpdeskSLA(models.Model):
    """SLA Policy for helpdesk tickets."""

    _name = "ipai.helpdesk.sla"
    _description = "Helpdesk SLA Policy"
    _order = "priority desc"

    name = fields.Char(required=True)
    team_id = fields.Many2one(
        "ipai.helpdesk.team",
        string="Team",
        required=True,
        ondelete="cascade",
    )
    active = fields.Boolean(default=True)

    # Matching Criteria
    priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Medium"),
            ("2", "High"),
            ("3", "Urgent"),
        ],
        string="Priority",
        required=True,
    )

    # SLA Target
    time_hours = fields.Float(
        string="Target Time (hours)",
        required=True,
        help="Time in hours to resolve the ticket",
    )
    time_days = fields.Float(
        string="Target Time (days)",
        compute="_compute_time_days",
        store=True,
    )

    # Escalation
    escalation_user_id = fields.Many2one(
        "res.users",
        string="Escalation User",
        help="User to notify when SLA is at risk",
    )
    warning_hours = fields.Float(
        string="Warning Before (hours)",
        default=2.0,
        help="Hours before deadline to send warning",
    )

    @api.depends("time_hours")
    def _compute_time_days(self):
        for sla in self:
            sla.time_days = sla.time_hours / 24 if sla.time_hours else 0

    _sql_constraints = [
        (
            "team_priority_unique",
            "UNIQUE(team_id, priority)",
            "Each priority can only have one SLA policy per team!",
        ),
    ]
