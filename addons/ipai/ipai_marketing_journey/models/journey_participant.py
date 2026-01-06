# -*- coding: utf-8 -*-
"""Marketing Journey Participant - state machine for journey participants."""

from odoo import api, fields, models


class MarketingJourneyParticipant(models.Model):
    """Participant in a marketing journey with state tracking."""

    _name = "marketing.journey.participant"
    _description = "Marketing Journey Participant"
    _order = "enrolled_date desc"
    _rec_name = "display_name"

    journey_id = fields.Many2one(
        "marketing.journey",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # Reference to participant record (generic)
    res_model = fields.Char(
        string="Model",
        required=True,
        index=True,
    )
    res_id = fields.Integer(
        string="Record ID",
        required=True,
        index=True,
    )

    # Denormalized fields for quick access
    email = fields.Char(index=True)
    name = fields.Char()
    display_name = fields.Char(compute="_compute_display_name", store=True)

    # State machine
    state = fields.Selection(
        [
            ("enrolled", "Enrolled"),
            ("in_progress", "In Progress"),
            ("waiting", "Waiting"),
            ("completed", "Completed"),
            ("exited", "Exited"),
            ("error", "Error"),
        ],
        default="enrolled",
        required=True,
        index=True,
    )

    # Current position in journey
    current_node_id = fields.Many2one(
        "marketing.journey.node",
        string="Current Node",
        index=True,
    )

    # Timing
    enrolled_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
    )
    last_action_date = fields.Datetime()
    wait_until = fields.Datetime(
        help="For delay nodes, when to resume processing",
    )
    completed_date = fields.Datetime()

    # Error tracking
    error_message = fields.Text()
    retry_count = fields.Integer(default=0)

    # History
    execution_log_ids = fields.One2many(
        "marketing.journey.execution.log",
        "participant_id",
        string="Execution History",
    )

    _sql_constraints = [
        (
            "unique_participant",
            "unique(journey_id, res_model, res_id)",
            "A record can only participate in a journey once.",
        ),
    ]

    @api.depends("name", "email", "res_model", "res_id")
    def _compute_display_name(self):
        for participant in self:
            if participant.name:
                participant.display_name = participant.name
            elif participant.email:
                participant.display_name = participant.email
            else:
                participant.display_name = f"{participant.res_model}/{participant.res_id}"

    def get_record(self):
        """Return the actual record this participant represents."""
        self.ensure_one()
        if self.res_model and self.res_id:
            return self.env[self.res_model].browse(self.res_id).exists()
        return None

    def action_exit(self):
        """Manually exit a participant from the journey."""
        self.write({"state": "exited"})

    def action_retry(self):
        """Retry a failed participant."""
        for participant in self:
            if participant.state == "error":
                participant.write({
                    "state": "in_progress",
                    "error_message": False,
                    "retry_count": participant.retry_count + 1,
                })

    def action_move_to_next(self):
        """Process this participant and move to next node."""
        self.ensure_one()
        runner = self.env["marketing.journey.runner"]
        return runner.process_participant(self)

    @api.model
    def create_from_record(self, journey, record):
        """
        Create a participant from a target record.

        Args:
            journey: marketing.journey record
            record: target model record (res.partner, mailing.contact, etc.)

        Returns:
            marketing.journey.participant record
        """
        email = getattr(record, "email", None)
        name = getattr(record, "name", None) or getattr(record, "display_name", None)

        return self.create({
            "journey_id": journey.id,
            "res_model": record._name,
            "res_id": record.id,
            "email": email,
            "name": name,
            "state": "enrolled",
        })

    def is_ready_to_process(self):
        """Check if participant is ready for next step."""
        self.ensure_one()

        # Already completed or exited
        if self.state in ("completed", "exited", "error"):
            return False

        # Waiting on delay
        if self.state == "waiting" and self.wait_until:
            if self.wait_until > fields.Datetime.now():
                return False

        return True
