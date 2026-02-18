# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing.

from odoo import models, fields, api


class HelpdeskTeam(models.Model):
    """Helpdesk Team for ticket routing and management."""

    _name = "ipai.helpdesk.team"
    _description = "Helpdesk Team"
    _inherit = ["mail.thread"]
    _order = "sequence, name"

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    color = fields.Integer(string="Color Index")

    # Team Members
    member_ids = fields.Many2many(
        "res.users",
        string="Team Members",
        help="Users who can be assigned tickets in this team",
    )
    leader_id = fields.Many2one(
        "res.users",
        string="Team Leader",
    )

    # Stages
    stage_ids = fields.Many2many(
        "ipai.helpdesk.stage",
        string="Stages",
        help="Stages available for tickets in this team",
    )

    # SLA Policies
    sla_policy_ids = fields.One2many(
        "ipai.helpdesk.sla",
        "team_id",
        string="SLA Policies",
    )

    # Assignment Settings
    auto_assign = fields.Boolean(
        string="Auto-Assignment",
        default=True,
        help="Automatically assign tickets to team members",
    )
    assign_method = fields.Selection(
        [
            ("random", "Random"),
            ("balanced", "Balanced (least tickets)"),
            ("round_robin", "Round Robin"),
            ("manual", "Manual"),
        ],
        string="Assignment Method",
        default="balanced",
    )
    last_assigned_id = fields.Many2one(
        "res.users",
        string="Last Assigned",
        help="For round-robin assignment tracking",
    )

    # Email Alias (for email-to-ticket)
    alias_name = fields.Char(string="Alias Name")
    alias_domain = fields.Char(
        string="Alias Domain",
        compute="_compute_alias_domain",
    )

    # Statistics
    ticket_count = fields.Integer(
        string="Tickets",
        compute="_compute_ticket_count",
    )
    ticket_open_count = fields.Integer(
        string="Open Tickets",
        compute="_compute_ticket_count",
    )

    @api.depends_context("company")
    def _compute_alias_domain(self):
        domain = self.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain")
        for team in self:
            team.alias_domain = domain or ""

    def _compute_ticket_count(self):
        for team in self:
            tickets = self.env["ipai.helpdesk.ticket"].search([
                ("team_id", "=", team.id)
            ])
            team.ticket_count = len(tickets)
            team.ticket_open_count = len(tickets.filtered(
                lambda t: not t.stage_id.is_close
            ))

    def _get_next_assignee(self):
        """Get the next user to assign a ticket to based on assignment method."""
        self.ensure_one()

        if not self.member_ids:
            return False

        if self.assign_method == "random":
            import random
            return random.choice(self.member_ids)

        elif self.assign_method == "balanced":
            # Assign to member with least open tickets
            ticket_counts = self.env["ipai.helpdesk.ticket"].read_group(
                [
                    ("team_id", "=", self.id),
                    ("user_id", "in", self.member_ids.ids),
                    ("stage_id.is_close", "=", False),
                ],
                ["user_id"],
                ["user_id"],
            )
            count_map = {r["user_id"][0]: r["user_id_count"] for r in ticket_counts if r["user_id"]}

            # Find member with least tickets (or no tickets)
            min_count = float("inf")
            best_member = self.member_ids[0]
            for member in self.member_ids:
                count = count_map.get(member.id, 0)
                if count < min_count:
                    min_count = count
                    best_member = member
            return best_member

        elif self.assign_method == "round_robin":
            # Get next member after last assigned
            members = list(self.member_ids)
            if self.last_assigned_id and self.last_assigned_id in members:
                idx = members.index(self.last_assigned_id)
                next_idx = (idx + 1) % len(members)
            else:
                next_idx = 0
            next_member = members[next_idx]
            self.last_assigned_id = next_member
            return next_member

        return False
