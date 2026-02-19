# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing.

from odoo import models, fields, api
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    """Helpdesk Ticket for tracking support requests."""

    _name = "ipai.helpdesk.ticket"
    _description = "Helpdesk Ticket"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _order = "priority desc, create_date desc"

    # Basic Info
    name = fields.Char(
        string="Subject",
        required=True,
        tracking=True,
    )
    description = fields.Html(string="Description")
    ticket_ref = fields.Char(
        string="Ticket Reference",
        readonly=True,
        copy=False,
        default=lambda self: "New",
    )

    # Classification
    team_id = fields.Many2one(
        "ipai.helpdesk.team",
        string="Team",
        required=True,
        tracking=True,
    )
    stage_id = fields.Many2one(
        "ipai.helpdesk.stage",
        string="Stage",
        tracking=True,
        group_expand="_read_group_stage_ids",
        domain="[('team_ids', 'in', team_id)]",
    )
    priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Medium"),
            ("2", "High"),
            ("3", "Urgent"),
        ],
        string="Priority",
        default="1",
        tracking=True,
    )
    tag_ids = fields.Many2many(
        "ipai.helpdesk.tag",
        string="Tags",
    )

    # Assignment
    user_id = fields.Many2one(
        "res.users",
        string="Assigned To",
        tracking=True,
    )

    # Customer
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
    )
    partner_email = fields.Char(
        string="Customer Email",
        related="partner_id.email",
        readonly=False,
    )
    partner_phone = fields.Char(
        string="Customer Phone",
        related="partner_id.phone",
        readonly=False,
    )

    # Company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    # SLA Tracking
    sla_deadline = fields.Datetime(
        string="SLA Deadline",
        compute="_compute_sla_deadline",
        store=True,
    )
    sla_status = fields.Selection(
        [
            ("ok", "On Track"),
            ("warning", "At Risk"),
            ("failed", "SLA Breached"),
        ],
        string="SLA Status",
        compute="_compute_sla_status",
        store=True,
    )
    sla_reached = fields.Boolean(
        string="SLA Reached",
        compute="_compute_sla_status",
        store=True,
    )
    sla_fail = fields.Boolean(
        string="SLA Failed",
        compute="_compute_sla_status",
        store=True,
    )

    # Time Tracking
    create_date = fields.Datetime(string="Created On", readonly=True)
    assign_date = fields.Datetime(string="Assigned On", readonly=True)
    first_response_date = fields.Datetime(string="First Response", readonly=True)
    close_date = fields.Datetime(string="Closed On", readonly=True)

    # Computed Time Metrics
    time_to_assign = fields.Float(
        string="Time to Assign (hours)",
        compute="_compute_time_metrics",
        store=True,
    )
    time_to_first_response = fields.Float(
        string="Time to First Response (hours)",
        compute="_compute_time_metrics",
        store=True,
    )
    time_to_close = fields.Float(
        string="Time to Close (hours)",
        compute="_compute_time_metrics",
        store=True,
    )

    # Status Flags
    is_closed = fields.Boolean(
        string="Is Closed",
        compute="_compute_is_closed",
        store=True,
    )
    kanban_state = fields.Selection(
        [
            ("normal", "Grey"),
            ("done", "Green"),
            ("blocked", "Red"),
        ],
        string="Kanban State",
        default="normal",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Create ticket with auto-assignment and SLA computation."""
        for vals in vals_list:
            if vals.get("ticket_ref", "New") == "New":
                vals["ticket_ref"] = self.env["ir.sequence"].next_by_code(
                    "ipai.helpdesk.ticket"
                ) or "New"

        tickets = super().create(vals_list)

        for ticket in tickets:
            # Auto-assign if enabled
            if ticket.team_id.auto_assign and not ticket.user_id:
                assignee = ticket.team_id._get_next_assignee()
                if assignee:
                    ticket.user_id = assignee
                    ticket.assign_date = fields.Datetime.now()

        return tickets

    def write(self, vals):
        """Track assignment and closure times."""
        # Track assignment
        if "user_id" in vals and vals.get("user_id"):
            for ticket in self:
                if not ticket.assign_date:
                    vals["assign_date"] = fields.Datetime.now()

        # Track closure
        if "stage_id" in vals:
            stage = self.env["ipai.helpdesk.stage"].browse(vals["stage_id"])
            if stage.is_close:
                vals["close_date"] = fields.Datetime.now()
            else:
                vals["close_date"] = False

        return super().write(vals)

    @api.depends("stage_id.is_close")
    def _compute_is_closed(self):
        for ticket in self:
            ticket.is_closed = ticket.stage_id.is_close if ticket.stage_id else False

    @api.depends("priority", "team_id", "create_date")
    def _compute_sla_deadline(self):
        """Compute SLA deadline based on priority and team SLA policies."""
        for ticket in self:
            if not ticket.team_id or not ticket.create_date:
                ticket.sla_deadline = False
                continue

            # Find matching SLA policy
            sla = ticket.team_id.sla_policy_ids.filtered(
                lambda s: s.priority == ticket.priority
            )[:1]

            if sla:
                ticket.sla_deadline = ticket.create_date + timedelta(hours=sla.time_hours)
            else:
                # Default SLA based on priority
                default_hours = {
                    "0": 72,  # Low: 72 hours
                    "1": 24,  # Medium: 24 hours
                    "2": 8,   # High: 8 hours
                    "3": 4,   # Urgent: 4 hours
                }
                hours = default_hours.get(ticket.priority, 24)
                ticket.sla_deadline = ticket.create_date + timedelta(hours=hours)

    @api.depends("sla_deadline", "close_date", "is_closed")
    def _compute_sla_status(self):
        """Compute SLA status based on deadline and current time."""
        now = fields.Datetime.now()
        for ticket in self:
            if not ticket.sla_deadline:
                ticket.sla_status = "ok"
                ticket.sla_reached = False
                ticket.sla_fail = False
                continue

            if ticket.is_closed:
                # Closed ticket: check if closed before deadline
                if ticket.close_date and ticket.close_date <= ticket.sla_deadline:
                    ticket.sla_status = "ok"
                    ticket.sla_reached = True
                    ticket.sla_fail = False
                else:
                    ticket.sla_status = "failed"
                    ticket.sla_reached = False
                    ticket.sla_fail = True
            else:
                # Open ticket: check current status
                if now > ticket.sla_deadline:
                    ticket.sla_status = "failed"
                    ticket.sla_reached = False
                    ticket.sla_fail = True
                elif now > ticket.sla_deadline - timedelta(hours=2):
                    ticket.sla_status = "warning"
                    ticket.sla_reached = False
                    ticket.sla_fail = False
                else:
                    ticket.sla_status = "ok"
                    ticket.sla_reached = False
                    ticket.sla_fail = False

    @api.depends("create_date", "assign_date", "first_response_date", "close_date")
    def _compute_time_metrics(self):
        """Compute time-based metrics."""
        for ticket in self:
            if ticket.create_date and ticket.assign_date:
                delta = ticket.assign_date - ticket.create_date
                ticket.time_to_assign = delta.total_seconds() / 3600
            else:
                ticket.time_to_assign = 0

            if ticket.create_date and ticket.first_response_date:
                delta = ticket.first_response_date - ticket.create_date
                ticket.time_to_first_response = delta.total_seconds() / 3600
            else:
                ticket.time_to_first_response = 0

            if ticket.create_date and ticket.close_date:
                delta = ticket.close_date - ticket.create_date
                ticket.time_to_close = delta.total_seconds() / 3600
            else:
                ticket.time_to_close = 0

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Ensure all stages are shown in Kanban view."""
        team_id = self._context.get("default_team_id")
        if team_id:
            search_domain = [("team_ids", "in", team_id)]
        else:
            search_domain = []
        return stages.search(search_domain, order=order)

    def action_open(self):
        """Open ticket details."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "ipai.helpdesk.ticket",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }


class HelpdeskTag(models.Model):
    """Tags for ticket categorization."""

    _name = "ipai.helpdesk.tag"
    _description = "Helpdesk Tag"

    name = fields.Char(required=True)
    color = fields.Integer(string="Color Index")
