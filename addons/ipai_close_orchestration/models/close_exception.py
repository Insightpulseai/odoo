from odoo import api, fields, models


class CloseException(models.Model):
    """Exception tracking for close cycle issues."""

    _name = "close.exception"
    _description = "Close Exception"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "severity desc, create_date desc"

    name = fields.Char(required=True, tracking=True)
    cycle_id = fields.Many2one(
        "close.cycle", required=True, ondelete="cascade", index=True
    )
    task_id = fields.Many2one("close.task", ondelete="set null", index=True)

    # Classification
    exception_type = fields.Selection(
        [
            ("missing_invoice", "Missing Invoice"),
            ("variance", "Unusual Variance"),
            ("unmatched", "Unmatched Transaction"),
            ("approval_delay", "Approval Delay"),
            ("doc_missing", "Missing Documentation"),
            ("posting_error", "Posting Error"),
            ("policy_violation", "Policy Violation"),
            ("system_error", "System Error"),
            ("other", "Other"),
        ],
        required=True,
        tracking=True,
    )

    severity = fields.Selection(
        [
            ("info", "Info"),
            ("warning", "Warning"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        default="warning",
        required=True,
        tracking=True,
    )

    # Status
    state = fields.Selection(
        [
            ("open", "Open"),
            ("investigating", "Investigating"),
            ("resolved", "Resolved"),
            ("cancelled", "Cancelled"),
        ],
        default="open",
        tracking=True,
    )

    # Details
    description = fields.Text()
    related_account_id = fields.Many2one("account.account")
    related_partner_id = fields.Many2one("res.partner")
    related_move_id = fields.Many2one("account.move", string="Related GL Entry")

    # Financial impact
    amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )
    variance_pct = fields.Float(string="Variance %")

    # Assignment
    detected_by = fields.Many2one("res.users", default=lambda self: self.env.user)
    detected_date = fields.Datetime(default=fields.Datetime.now)
    assigned_to = fields.Many2one("res.users", tracking=True)

    # Resolution
    root_cause = fields.Text()
    resolution_action = fields.Text()
    resolved_by = fields.Many2one("res.users")
    resolved_date = fields.Datetime()

    # Escalation
    escalation_level = fields.Integer(default=0)
    escalated_to = fields.Many2one("res.users")
    escalated_date = fields.Datetime()

    def action_investigate(self):
        """Start investigation."""
        self.ensure_one()
        self.state = "investigating"
        self.message_post(body=f"Investigation started by {self.env.user.name}")

    def action_resolve(self):
        """Resolve exception."""
        self.ensure_one()
        self.state = "resolved"
        self.resolved_by = self.env.user
        self.resolved_date = fields.Datetime.now()
        self.message_post(
            body=f"Exception resolved: {self.resolution_action or 'See notes'}"
        )

    def action_escalate(self):
        """Escalate to next level."""
        self.ensure_one()
        self.escalation_level += 1
        self.escalated_date = fields.Datetime.now()

        # Determine escalation target based on level
        if self.escalation_level == 1:
            # Escalate to BOM
            role = "bom"
        elif self.escalation_level == 2:
            # Escalate to CKVC
            role = "ckvc"
        else:
            # Escalate to FD
            role = "fd"

        self.message_post(body=f"Exception escalated to level {self.escalation_level}")

    def action_cancel(self):
        """Cancel exception (false positive)."""
        self.ensure_one()
        self.state = "cancelled"
        self.message_post(body="Exception cancelled (false positive)")

    @api.model
    def _cron_auto_escalate(self):
        """Auto-escalate exceptions that have been open too long."""
        from datetime import timedelta as td

        # Escalation thresholds (hours)
        ESCALATION_HOURS = {
            "critical": 4,  # Escalate critical after 4 hours
            "high": 24,  # Escalate high after 24 hours
            "warning": 48,  # Escalate warning after 48 hours
        }

        now = fields.Datetime.now()

        for severity, hours in ESCALATION_HOURS.items():
            threshold = now - td(hours=hours)
            exceptions_to_escalate = self.search(
                [
                    ("state", "in", ("open", "investigating")),
                    ("severity", "=", severity),
                    ("detected_date", "<", threshold),
                    ("escalation_level", "<", 3),  # Max 3 escalation levels
                ]
            )

            for exc in exceptions_to_escalate:
                exc.action_escalate()
                exc.message_post(
                    body=f"Auto-escalated due to {hours}+ hours without resolution"
                )
