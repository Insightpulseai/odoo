"""IPAI Tax Intelligence — Tax Audit Log model.

Immutable append-only audit trail for all tax exception state transitions
and computation events.

Constitution Principle 3: Every Pulser tax action must have a reversible audit trace.
Constitution Principle 1: Odoo owns the audit record.
"""

from odoo import fields, models


class TaxAuditLog(models.Model):
    _name = "tax.audit.log"
    _description = "Tax Audit Log"
    _order = "timestamp desc, id desc"

    # Audit logs are immutable — no write/unlink for non-admin
    exception_id = fields.Many2one(
        "tax.exception",
        string="Tax Exception",
        required=True,
        ondelete="cascade",
        index=True,
    )
    timestamp = fields.Datetime(
        string="Timestamp",
        required=True,
        default=fields.Datetime.now,
        readonly=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        default=lambda self: self.env.uid,
        readonly=True,
    )
    action = fields.Selection(
        [
            ("created", "Created"),
            ("review_started", "Review Started"),
            ("resolved", "Resolved"),
            ("waived", "Waived"),
            ("escalated", "Escalated"),
            ("reopened", "Reopened"),
        ],
        string="Action",
        required=True,
        readonly=True,
    )
    old_state = fields.Char(
        string="Previous State",
        readonly=True,
    )
    new_state = fields.Char(
        string="New State",
        required=True,
        readonly=True,
    )
    notes = fields.Text(
        string="Notes",
        help="Additional context about this audit event.",
    )
    computation_detail = fields.Text(
        string="Computation Detail",
        help="Structured detail of the tax computation inputs and outputs at the time of this event.",
    )
