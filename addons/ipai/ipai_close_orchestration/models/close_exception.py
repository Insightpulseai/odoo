# -*- coding: utf-8 -*-
"""
Close Exception

Issue tracking and escalation for close tasks.
"""
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CloseException(models.Model):
    """
    Exception/issue raised during close process.
    """

    _name = "close.exception"
    _description = "Close Exception"
    _order = "create_date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Core fields
    name = fields.Char(
        string="Title",
        required=True,
        tracking=True,
    )
    description = fields.Html(string="Description")

    # Classification
    exception_type = fields.Selection([
        ("data", "Data Issue"),
        ("timing", "Timing Issue"),
        ("process", "Process Deviation"),
        ("system", "System Error"),
        ("other", "Other"),
    ], string="Type", default="other", required=True, tracking=True)

    severity = fields.Selection([
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ], string="Severity", default="medium", required=True, tracking=True)

    # Status
    state = fields.Selection([
        ("open", "Open"),
        ("investigating", "Investigating"),
        ("escalated", "Escalated"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ], string="State", default="open", tracking=True, required=True)

    # Relationships
    cycle_id = fields.Many2one(
        "close.cycle",
        string="Close Cycle",
        required=True,
        ondelete="cascade",
        index=True,
    )
    task_id = fields.Many2one(
        "close.task",
        string="Related Task",
        ondelete="set null",
        index=True,
    )

    # Assignment
    reported_by = fields.Many2one(
        "res.users",
        string="Reported By",
        default=lambda self: self.env.user,
        tracking=True,
    )
    assigned_to = fields.Many2one(
        "res.users",
        string="Assigned To",
        tracking=True,
    )
    escalated_to = fields.Many2one(
        "res.users",
        string="Escalated To",
        tracking=True,
    )

    # Escalation tracking
    escalation_count = fields.Integer(string="Escalation Count", default=0)
    last_escalated = fields.Datetime(string="Last Escalated")
    escalation_deadline = fields.Datetime(
        string="Escalation Deadline",
        help="Auto-escalate if not resolved by this time",
    )

    # Resolution
    resolution = fields.Html(string="Resolution")
    resolved_date = fields.Datetime(string="Resolved At")
    resolved_by = fields.Many2one("res.users", string="Resolved By")

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="cycle_id.company_id",
        store=True,
    )

    def action_start_investigation(self):
        """Start investigating the exception."""
        self.ensure_one()
        if self.state != "open":
            return
        self.state = "investigating"
        self.message_post(body=f"Investigation started by {self.env.user.name}")

    def action_escalate(self):
        """Escalate the exception."""
        self.ensure_one()
        self.write({
            "state": "escalated",
            "escalation_count": self.escalation_count + 1,
            "last_escalated": fields.Datetime.now(),
        })
        self.message_post(body=f"Escalated by {self.env.user.name}")

        # Notify escalated_to user
        if self.escalated_to:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=self.escalated_to.id,
                summary=f"Escalated exception: {self.name}",
            )

    def action_resolve(self):
        """Mark exception as resolved."""
        self.ensure_one()
        self.write({
            "state": "resolved",
            "resolved_date": fields.Datetime.now(),
            "resolved_by": self.env.user.id,
        })
        self.message_post(body=f"Resolved by {self.env.user.name}")

    def action_close(self):
        """Close the exception."""
        self.ensure_one()
        if self.state != "resolved":
            return
        self.state = "closed"
        self.message_post(body=f"Closed by {self.env.user.name}")

    def action_reopen(self):
        """Reopen a closed exception."""
        self.ensure_one()
        if self.state not in ("resolved", "closed"):
            return
        self.state = "open"
        self.message_post(body=f"Reopened by {self.env.user.name}")

    @api.model
    def _cron_auto_escalate(self):
        """Auto-escalate exceptions past their deadline."""
        now = fields.Datetime.now()

        exceptions = self.search([
            ("state", "in", ("open", "investigating")),
            ("escalation_deadline", "<=", now),
        ])

        for exc in exceptions:
            exc.write({
                "state": "escalated",
                "escalation_count": exc.escalation_count + 1,
                "last_escalated": now,
            })
            exc.message_post(body="Auto-escalated due to deadline")

            # Notify cycle owner
            if exc.cycle_id.a1_tasklist_id:
                tasklist = exc.cycle_id.a1_tasklist_id
                if tasklist.create_uid:
                    exc.activity_schedule(
                        "mail.mail_activity_data_todo",
                        user_id=tasklist.create_uid.id,
                        summary=f"Auto-escalated: {exc.name}",
                    )

        if exceptions:
            _logger.info("Auto-escalated %d exceptions", len(exceptions))
