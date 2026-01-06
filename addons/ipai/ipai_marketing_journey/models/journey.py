# -*- coding: utf-8 -*-
"""Marketing Journey - main workflow definition."""

from odoo import api, fields, models
from odoo.exceptions import UserError


class MarketingJourney(models.Model):
    """Marketing automation journey definition."""

    _name = "marketing.journey"
    _description = "Marketing Journey"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    description = fields.Text()
    active = fields.Boolean(default=True, tracking=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("running", "Running"),
            ("paused", "Paused"),
            ("stopped", "Stopped"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # Target configuration
    model_id = fields.Many2one(
        "ir.model",
        string="Target Model",
        domain=[("model", "in", ["res.partner", "crm.lead", "mailing.contact"])],
        required=True,
        help="Model that participants are based on (contacts, leads, etc.)",
    )
    domain = fields.Text(
        default="[]",
        help="Domain filter for selecting eligible participants",
    )
    unique_field_id = fields.Many2one(
        "ir.model.fields",
        string="Unique Field",
        help="Field to use for participant uniqueness (default: email)",
    )

    # UTM tracking
    campaign_id = fields.Many2one("utm.campaign", string="UTM Campaign")
    source_id = fields.Many2one("utm.source", string="UTM Source")
    medium_id = fields.Many2one("utm.medium", string="UTM Medium")

    # Nodes and edges
    node_ids = fields.One2many("marketing.journey.node", "journey_id", string="Nodes")
    edge_ids = fields.One2many("marketing.journey.edge", "journey_id", string="Edges")

    # Participants
    participant_ids = fields.One2many(
        "marketing.journey.participant",
        "journey_id",
        string="Participants",
    )
    participant_count = fields.Integer(
        compute="_compute_participant_stats", store=True
    )
    active_participant_count = fields.Integer(
        compute="_compute_participant_stats", store=True
    )
    completed_participant_count = fields.Integer(
        compute="_compute_participant_stats", store=True
    )

    # Execution logs
    execution_log_ids = fields.One2many(
        "marketing.journey.execution.log",
        "journey_id",
        string="Execution Logs",
    )

    # Statistics
    start_date = fields.Datetime(tracking=True)
    end_date = fields.Datetime(tracking=True)
    last_run = fields.Datetime(readonly=True)

    @api.depends("participant_ids", "participant_ids.state")
    def _compute_participant_stats(self):
        for journey in self:
            participants = journey.participant_ids
            journey.participant_count = len(participants)
            journey.active_participant_count = len(
                participants.filtered(lambda p: p.state == "in_progress")
            )
            journey.completed_participant_count = len(
                participants.filtered(lambda p: p.state == "completed")
            )

    def action_start(self):
        """Start the journey and begin enrolling participants."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Only draft journeys can be started.")

        # Validate journey has at least one node
        if not self.node_ids:
            raise UserError("Journey must have at least one node to start.")

        # Find entry node
        entry_nodes = self.node_ids.filtered(lambda n: n.is_entry)
        if not entry_nodes:
            raise UserError("Journey must have an entry node.")

        self.write(
            {
                "state": "running",
                "start_date": fields.Datetime.now(),
            }
        )
        self.message_post(body="Journey started.")
        return True

    def action_pause(self):
        """Pause the journey (stop enrollments, pause executions)."""
        self.ensure_one()
        if self.state != "running":
            raise UserError("Only running journeys can be paused.")
        self.write({"state": "paused"})
        self.message_post(body="Journey paused.")
        return True

    def action_resume(self):
        """Resume a paused journey."""
        self.ensure_one()
        if self.state != "paused":
            raise UserError("Only paused journeys can be resumed.")
        self.write({"state": "running"})
        self.message_post(body="Journey resumed.")
        return True

    def action_stop(self):
        """Stop the journey completely."""
        self.ensure_one()
        if self.state not in ("running", "paused"):
            raise UserError("Only running or paused journeys can be stopped.")
        self.write(
            {
                "state": "stopped",
                "end_date": fields.Datetime.now(),
            }
        )
        self.message_post(body="Journey stopped.")
        return True

    def action_reset_to_draft(self):
        """Reset journey to draft (removes all participants)."""
        self.ensure_one()
        if self.state != "stopped":
            raise UserError("Only stopped journeys can be reset.")

        # Remove all participants
        self.participant_ids.unlink()
        self.execution_log_ids.unlink()

        self.write(
            {
                "state": "draft",
                "start_date": False,
                "end_date": False,
                "last_run": False,
            }
        )
        self.message_post(body="Journey reset to draft.")
        return True

    def action_enroll_participants(self):
        """Manually trigger participant enrollment."""
        self.ensure_one()
        if self.state != "running":
            raise UserError("Only running journeys can enroll participants.")

        runner = self.env["marketing.journey.runner"]
        count = runner.enroll_participants(self)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Enrollment Complete",
                "message": f"{count} new participants enrolled.",
                "type": "success",
            },
        }

    def action_view_participants(self):
        """Open participant list view."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Participants",
            "res_model": "marketing.journey.participant",
            "view_mode": "tree,form",
            "domain": [("journey_id", "=", self.id)],
            "context": {"default_journey_id": self.id},
        }

    def get_entry_node(self):
        """Return the entry node for this journey."""
        self.ensure_one()
        return self.node_ids.filtered(lambda n: n.is_entry)[:1]

    @api.model
    def get_model_domain(self):
        """Return list of valid target models."""
        return [
            ("res.partner", "Contacts"),
            ("mailing.contact", "Mailing Contacts"),
        ]
