# -*- coding: utf-8 -*-
"""Marketing Journey Node - individual steps in a journey."""

from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class MarketingJourneyNode(models.Model):
    """Single node/step in a marketing journey."""

    _name = "marketing.journey.node"
    _description = "Marketing Journey Node"
    _order = "sequence, id"

    name = fields.Char(required=True)
    journey_id = fields.Many2one(
        "marketing.journey",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)

    node_type = fields.Selection(
        [
            ("entry", "Entry Point"),
            ("email", "Send Email"),
            ("sms", "Send SMS"),
            ("delay", "Wait/Delay"),
            ("branch", "Branch/Condition"),
            ("action", "Server Action"),
            ("tag", "Add/Remove Tag"),
            ("activity", "Create Activity"),
            ("exit", "Exit Journey"),
        ],
        required=True,
        default="email",
    )

    is_entry = fields.Boolean(
        compute="_compute_is_entry",
        store=True,
        help="Is this the entry point node?",
    )
    is_exit = fields.Boolean(
        compute="_compute_is_exit",
        store=True,
        help="Is this an exit node?",
    )

    # Position for visual builder (future)
    position_x = fields.Integer(default=0)
    position_y = fields.Integer(default=0)

    # Email configuration
    mailing_id = fields.Many2one(
        "mailing.mailing",
        string="Email Template",
        help="Mass mailing to send",
    )

    # Delay configuration
    delay_value = fields.Integer(default=1, help="Number of time units")
    delay_unit = fields.Selection(
        [
            ("minutes", "Minutes"),
            ("hours", "Hours"),
            ("days", "Days"),
            ("weeks", "Weeks"),
        ],
        default="days",
    )

    # Branch configuration
    branch_domain = fields.Text(
        default="[]",
        help="Domain for TRUE branch (participants matching will go to true_edge)",
    )

    # Action configuration
    server_action_id = fields.Many2one(
        "ir.actions.server",
        string="Server Action",
        help="Server action to execute",
    )

    # Tag configuration
    tag_action = fields.Selection(
        [("add", "Add Tag"), ("remove", "Remove Tag")],
        default="add",
    )
    partner_tag_ids = fields.Many2many(
        "res.partner.category",
        string="Partner Tags",
    )

    # Activity configuration
    activity_type_id = fields.Many2one(
        "mail.activity.type",
        string="Activity Type",
    )
    activity_summary = fields.Char(string="Activity Summary")
    activity_user_id = fields.Many2one(
        "res.users",
        string="Assigned To",
    )

    # Edges (connections)
    outgoing_edge_ids = fields.One2many(
        "marketing.journey.edge",
        "source_node_id",
        string="Outgoing Edges",
    )
    incoming_edge_ids = fields.One2many(
        "marketing.journey.edge",
        "target_node_id",
        string="Incoming Edges",
    )

    # Statistics
    participant_count = fields.Integer(compute="_compute_stats", store=True)
    success_count = fields.Integer(compute="_compute_stats", store=True)
    error_count = fields.Integer(compute="_compute_stats", store=True)

    @api.depends("node_type")
    def _compute_is_entry(self):
        for node in self:
            node.is_entry = node.node_type == "entry"

    @api.depends("node_type")
    def _compute_is_exit(self):
        for node in self:
            node.is_exit = node.node_type == "exit"

    @api.depends("journey_id.participant_ids.current_node_id")
    def _compute_stats(self):
        for node in self:
            logs = self.env["marketing.journey.execution.log"].search(
                [("node_id", "=", node.id)]
            )
            node.participant_count = len(logs)
            node.success_count = len(logs.filtered(lambda l: l.state == "success"))
            node.error_count = len(logs.filtered(lambda l: l.state == "error"))

    def get_delay_timedelta(self):
        """Return timedelta for delay nodes."""
        self.ensure_one()
        if self.node_type != "delay":
            return timedelta()

        mapping = {
            "minutes": timedelta(minutes=self.delay_value),
            "hours": timedelta(hours=self.delay_value),
            "days": timedelta(days=self.delay_value),
            "weeks": timedelta(weeks=self.delay_value),
        }
        return mapping.get(self.delay_unit, timedelta())

    def get_next_nodes(self, participant=None):
        """
        Get next nodes based on edges.

        For branch nodes, evaluate condition and return appropriate edge.
        For other nodes, return all outgoing edges' targets.

        Args:
            participant: marketing.journey.participant record for branch evaluation

        Returns:
            recordset of marketing.journey.node
        """
        self.ensure_one()

        if self.node_type == "branch" and participant:
            # Evaluate branch condition
            domain = eval(self.branch_domain or "[]")
            record = participant.get_record()

            if record:
                # Check if record matches domain
                Model = self.env[participant.journey_id.model_id.model]
                matching = Model.search([("id", "=", record.id)] + domain)

                if matching:
                    # TRUE branch
                    edge = self.outgoing_edge_ids.filtered(
                        lambda e: e.edge_type == "true"
                    )[:1]
                else:
                    # FALSE branch
                    edge = self.outgoing_edge_ids.filtered(
                        lambda e: e.edge_type == "false"
                    )[:1]

                return (
                    edge.target_node_id if edge else self.env["marketing.journey.node"]
                )

        # Default: return all outgoing targets
        return self.outgoing_edge_ids.mapped("target_node_id")

    def execute(self, participant):
        """
        Execute this node for a participant.

        Args:
            participant: marketing.journey.participant record

        Returns:
            dict with execution result
        """
        self.ensure_one()

        method_name = f"_execute_{self.node_type}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(participant)

        return {"success": True, "message": f"Node type {self.node_type} executed"}

    def _execute_entry(self, participant):
        """Entry node - just passes through."""
        return {"success": True, "message": "Entry point reached"}

    def _execute_exit(self, participant):
        """Exit node - marks participant as completed."""
        participant.write({"state": "completed"})
        return {"success": True, "message": "Journey completed"}

    def _execute_email(self, participant):
        """Send email via mass_mailing."""
        if not self.mailing_id:
            return {"success": False, "error": "No email template configured"}

        record = participant.get_record()
        if not record:
            return {"success": False, "error": "Participant record not found"}

        try:
            # Create a trace for this specific send
            email = getattr(record, "email", None)
            if not email:
                return {"success": False, "error": "No email address found"}

            # Use mass_mailing's send mechanism
            self.mailing_id.with_context(default_res_id=record.id).action_send_mail()

            return {
                "success": True,
                "message": f"Email '{self.mailing_id.subject}' sent to {email}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_delay(self, participant):
        """Set participant to wait for delay period."""
        wait_until = fields.Datetime.now() + self.get_delay_timedelta()
        participant.write(
            {
                "state": "waiting",
                "wait_until": wait_until,
            }
        )
        return {
            "success": True,
            "message": f"Waiting until {wait_until}",
            "wait_until": wait_until,
        }

    def _execute_branch(self, participant):
        """Branch node - evaluation happens in get_next_nodes."""
        return {"success": True, "message": "Branch evaluated"}

    def _execute_action(self, participant):
        """Execute server action."""
        if not self.server_action_id:
            return {"success": False, "error": "No server action configured"}

        record = participant.get_record()
        if not record:
            return {"success": False, "error": "Participant record not found"}

        try:
            self.server_action_id.with_context(
                active_id=record.id,
                active_ids=[record.id],
                active_model=participant.journey_id.model_id.model,
            ).run()
            return {"success": True, "message": "Server action executed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_tag(self, participant):
        """Add or remove partner tags."""
        record = participant.get_record()
        if not record:
            return {"success": False, "error": "Participant record not found"}

        # Only works for res.partner
        if participant.journey_id.model_id.model != "res.partner":
            return {"success": False, "error": "Tags only supported for partners"}

        if not self.partner_tag_ids:
            return {"success": False, "error": "No tags configured"}

        try:
            if self.tag_action == "add":
                record.write(
                    {"category_id": [(4, tag.id) for tag in self.partner_tag_ids]}
                )
                return {"success": True, "message": "Tags added"}
            else:
                record.write(
                    {"category_id": [(3, tag.id) for tag in self.partner_tag_ids]}
                )
                return {"success": True, "message": "Tags removed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_activity(self, participant):
        """Create activity for the participant."""
        if not self.activity_type_id:
            return {"success": False, "error": "No activity type configured"}

        record = participant.get_record()
        if not record:
            return {"success": False, "error": "Participant record not found"}

        try:
            self.env["mail.activity"].create(
                {
                    "activity_type_id": self.activity_type_id.id,
                    "summary": self.activity_summary or self.name,
                    "res_model_id": participant.journey_id.model_id.id,
                    "res_id": record.id,
                    "user_id": self.activity_user_id.id or self.env.uid,
                }
            )
            return {"success": True, "message": "Activity created"}
        except Exception as e:
            return {"success": False, "error": str(e)}
