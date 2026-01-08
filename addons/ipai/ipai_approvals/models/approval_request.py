# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IPAIApprovalRequest(models.Model):
    """
    Approval Request represents a single approval workflow instance.

    State machine:
    - draft: Request created, not yet submitted
    - pending: Submitted, waiting for approvals
    - approved: All required approvals received
    - rejected: Rejected by an approver
    - cancelled: Cancelled by requester
    """
    _name = "ipai.approval.request"
    _description = "Approval Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("New"),
        copy=False
    )
    type_id = fields.Many2one(
        "ipai.approval.type",
        required=True,
        tracking=True,
        string="Approval Type"
    )
    company_id = fields.Many2one(
        "res.company",
        related="type_id.company_id",
        store=True
    )
    user_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
        string="Requester"
    )

    # Reference to approved record
    res_model = fields.Char(string="Model", tracking=True)
    res_id = fields.Integer(string="Record ID", tracking=True)
    res_name = fields.Char(compute="_compute_res_name", string="Record")

    # Request details
    description = fields.Html(string="Description")
    amount = fields.Float(help="Amount for threshold-based auto-approval")
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id
    )

    # State
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
        required=True
    )

    # Approver tracking
    approver_ids = fields.One2many(
        "ipai.approval.approver",
        "request_id",
        string="Approvers"
    )
    approval_count = fields.Integer(
        compute="_compute_approval_count",
        string="Approvals"
    )
    required_approvals = fields.Integer(
        related="type_id.minimum_approvers"
    )

    # Dates
    date_submitted = fields.Datetime(tracking=True)
    date_approved = fields.Datetime(tracking=True)
    date_rejected = fields.Datetime(tracking=True)

    # Final decision
    final_approver_id = fields.Many2one(
        "res.users",
        string="Final Decision By",
        tracking=True
    )
    rejection_reason = fields.Text(tracking=True)

    @api.depends("res_model", "res_id")
    def _compute_res_name(self):
        for rec in self:
            if rec.res_model and rec.res_id:
                try:
                    record = self.env[rec.res_model].browse(rec.res_id)
                    rec.res_name = record.display_name if record.exists() else False
                except Exception:
                    rec.res_name = False
            else:
                rec.res_name = False

    @api.depends("approver_ids.state")
    def _compute_approval_count(self):
        for rec in self:
            rec.approval_count = len(rec.approver_ids.filtered(
                lambda a: a.state == "approved"
            ))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "ipai.approval.request"
                ) or _("New")
        return super().create(vals_list)

    def action_submit(self):
        """Submit the request for approval."""
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only draft requests can be submitted."))

            # Check for auto-approval based on amount threshold
            if rec.type_id.auto_approve_amount > 0 and rec.amount <= rec.type_id.auto_approve_amount:
                rec._auto_approve()
                continue

            # Get approvers and create approver records
            approvers = rec.type_id.get_approvers(rec)
            if not approvers:
                raise UserError(_("No approvers configured for this approval type."))

            for user in approvers:
                self.env["ipai.approval.approver"].create({
                    "request_id": rec.id,
                    "user_id": user.id,
                })

            rec.write({
                "state": "pending",
                "date_submitted": fields.Datetime.now(),
            })

            # Send notifications
            if rec.type_id.notify_on_request:
                rec._send_notification("pending")

            # Create activities
            if rec.type_id.create_activity:
                rec._create_approval_activities()

            rec.message_post(body=_("Request submitted for approval."))

    def action_approve(self):
        """Approve the request (for current user)."""
        self.ensure_one()
        if self.state != "pending":
            raise UserError(_("Only pending requests can be approved."))

        approver = self.approver_ids.filtered(
            lambda a: a.user_id == self.env.user and a.state == "pending"
        )
        if not approver:
            raise UserError(_("You are not an approver for this request or have already decided."))

        approver.action_approve()
        self._check_approval_complete()

    def action_reject(self, reason=None):
        """Reject the request."""
        self.ensure_one()
        if self.state != "pending":
            raise UserError(_("Only pending requests can be rejected."))

        approver = self.approver_ids.filtered(
            lambda a: a.user_id == self.env.user and a.state == "pending"
        )
        if not approver:
            raise UserError(_("You are not an approver for this request or have already decided."))

        approver.action_reject(reason)

        self.write({
            "state": "rejected",
            "date_rejected": fields.Datetime.now(),
            "final_approver_id": self.env.user.id,
            "rejection_reason": reason,
        })

        if self.type_id.notify_on_reject:
            self._send_notification("rejected")

        # Remove pending activities
        self.activity_ids.filtered(lambda a: a.activity_type_id == self.type_id.activity_type_id).unlink()

        self.message_post(body=_("Request rejected by %s. Reason: %s") % (
            self.env.user.name,
            reason or _("No reason provided")
        ))

    def action_cancel(self):
        """Cancel the request."""
        for rec in self:
            if rec.state in ("approved", "rejected"):
                raise UserError(_("Cannot cancel a finalized request."))

            rec.state = "cancelled"
            rec.activity_ids.unlink()
            rec.message_post(body=_("Request cancelled."))

    def action_reset_to_draft(self):
        """Reset a cancelled/rejected request to draft."""
        for rec in self:
            if rec.state not in ("cancelled", "rejected"):
                raise UserError(_("Only cancelled or rejected requests can be reset."))

            rec.approver_ids.unlink()
            rec.write({
                "state": "draft",
                "date_submitted": False,
                "date_approved": False,
                "date_rejected": False,
                "final_approver_id": False,
                "rejection_reason": False,
            })
            rec.message_post(body=_("Request reset to draft."))

    def _check_approval_complete(self):
        """Check if enough approvals have been received."""
        self.ensure_one()
        approved_count = len(self.approver_ids.filtered(lambda a: a.state == "approved"))

        if self.type_id.require_all:
            # Need all approvers to approve
            pending = self.approver_ids.filtered(lambda a: a.state == "pending")
            if not pending:
                self._finalize_approval()
        else:
            # Need minimum number of approvals
            if approved_count >= self.type_id.minimum_approvers:
                self._finalize_approval()

    def _finalize_approval(self):
        """Finalize the approval."""
        self.write({
            "state": "approved",
            "date_approved": fields.Datetime.now(),
            "final_approver_id": self.env.user.id,
        })

        if self.type_id.notify_on_approve:
            self._send_notification("approved")

        # Remove pending activities
        self.activity_ids.filtered(
            lambda a: a.activity_type_id == self.type_id.activity_type_id
        ).unlink()

        self.message_post(body=_("Request approved."))

    def _auto_approve(self):
        """Auto-approve based on threshold."""
        self.write({
            "state": "approved",
            "date_submitted": fields.Datetime.now(),
            "date_approved": fields.Datetime.now(),
        })
        self.message_post(body=_("Request auto-approved (amount below threshold)."))

    def _send_notification(self, notification_type):
        """Send email notification."""
        template_map = {
            "pending": "ipai_approvals.mail_template_approval_request_pending",
            "approved": "ipai_approvals.mail_template_approval_request_approved",
            "rejected": "ipai_approvals.mail_template_approval_request_rejected",
        }
        template_xmlid = template_map.get(notification_type)
        if template_xmlid:
            template = self.env.ref(template_xmlid, raise_if_not_found=False)
            if template:
                template.send_mail(self.id, force_send=True)

    def _create_approval_activities(self):
        """Create activities for pending approvers."""
        if not self.type_id.activity_type_id:
            return

        for approver in self.approver_ids.filtered(lambda a: a.state == "pending"):
            self.activity_schedule(
                activity_type_id=self.type_id.activity_type_id.id,
                summary=_("Approval Required: %s") % self.name,
                user_id=approver.user_id.id,
            )

    def action_open_record(self):
        """Open the linked record."""
        self.ensure_one()
        if not self.res_model or not self.res_id:
            raise UserError(_("No linked record."))

        return {
            "type": "ir.actions.act_window",
            "res_model": self.res_model,
            "res_id": self.res_id,
            "view_mode": "form",
            "target": "current",
        }
