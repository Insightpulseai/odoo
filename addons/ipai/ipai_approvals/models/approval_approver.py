# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class IPAIApprovalApprover(models.Model):
    """
    Tracks individual approver decisions on an approval request.
    """

    _name = "ipai.approval.approver"
    _description = "Approval Approver"
    _order = "sequence, id"

    request_id = fields.Many2one(
        "ipai.approval.request", required=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=10)
    user_id = fields.Many2one("res.users", required=True, string="Approver")

    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("delegated", "Delegated"),
        ],
        default="pending",
        required=True,
    )

    # Decision tracking
    decision_date = fields.Datetime()
    notes = fields.Text(string="Comments")

    # Delegation
    delegated_to_id = fields.Many2one("res.users", string="Delegated To")
    delegated_from_id = fields.Many2one("res.users", string="Delegated From")

    # Computed
    can_approve = fields.Boolean(compute="_compute_can_approve")

    @api.depends("user_id", "state")
    def _compute_can_approve(self):
        for rec in self:
            rec.can_approve = rec.user_id == self.env.user and rec.state == "pending"

    def action_approve(self, notes=None):
        """Record approval decision."""
        self.ensure_one()
        self.write(
            {
                "state": "approved",
                "decision_date": fields.Datetime.now(),
                "notes": notes,
            }
        )
        self.request_id.message_post(
            body=_("Approved by %s.%s")
            % (self.user_id.name, f" Notes: {notes}" if notes else "")
        )

    def action_reject(self, reason=None):
        """Record rejection decision."""
        self.ensure_one()
        self.write(
            {
                "state": "rejected",
                "decision_date": fields.Datetime.now(),
                "notes": reason,
            }
        )

    def action_delegate(self, delegate_to_user):
        """Delegate approval to another user."""
        self.ensure_one()
        if not delegate_to_user:
            return

        # Mark current approver as delegated
        self.write(
            {
                "state": "delegated",
                "delegated_to_id": delegate_to_user.id,
                "decision_date": fields.Datetime.now(),
            }
        )

        # Create new approver record for delegate
        self.env["ipai.approval.approver"].create(
            {
                "request_id": self.request_id.id,
                "user_id": delegate_to_user.id,
                "delegated_from_id": self.user_id.id,
                "sequence": self.sequence,
            }
        )

        self.request_id.message_post(
            body=_("%s delegated approval to %s.")
            % (self.user_id.name, delegate_to_user.name)
        )

        # Create activity for new approver
        if self.request_id.type_id.create_activity:
            self.request_id.activity_schedule(
                activity_type_id=self.request_id.type_id.activity_type_id.id,
                summary=_("Approval Delegated: %s") % self.request_id.name,
                user_id=delegate_to_user.id,
            )
