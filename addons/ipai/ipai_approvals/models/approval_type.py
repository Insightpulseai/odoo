# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IPAIApprovalType(models.Model):
    """
    Approval Type defines a workflow template for approvals.

    Each type specifies:
    - Which model requires approval
    - Who can approve (users, groups, manager chain)
    - How many approvals are needed
    - Notification settings
    """
    _name = "ipai.approval.type"
    _description = "Approval Type"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True
    )
    description = fields.Html(translate=True)

    # Target model
    res_model = fields.Char(
        string="Model",
        help="Technical name of the model requiring approval (e.g., purchase.order)"
    )
    res_model_id = fields.Many2one(
        "ir.model",
        string="Model (UI)",
        ondelete="cascade",
        domain=[("transient", "=", False)]
    )

    # Approval settings
    approval_type = fields.Selection(
        [
            ("user", "Specific Users"),
            ("group", "Security Group"),
            ("manager", "Manager Chain"),
            ("custom", "Custom (via matrix)"),
        ],
        default="user",
        required=True
    )

    # Approvers (when type = user)
    approver_ids = fields.Many2many(
        "res.users",
        "ipai_approval_type_user_rel",
        "type_id",
        "user_id",
        string="Approvers"
    )

    # Approver group (when type = group)
    approver_group_id = fields.Many2one(
        "res.groups",
        string="Approver Group"
    )

    # Manager levels (when type = manager)
    manager_levels = fields.Integer(
        default=1,
        help="Number of management levels to involve (1 = direct manager, 2 = manager's manager, etc.)"
    )

    # Approval requirements
    minimum_approvers = fields.Integer(
        default=1,
        help="Minimum number of approvals required before the request is approved"
    )
    require_all = fields.Boolean(
        string="Require All Approvers",
        help="If checked, ALL designated approvers must approve (ignores minimum_approvers)"
    )

    # Notifications
    notify_on_request = fields.Boolean(
        default=True,
        help="Send email to approvers when a new request is created"
    )
    notify_on_approve = fields.Boolean(
        default=True,
        help="Send email to requester when request is approved"
    )
    notify_on_reject = fields.Boolean(
        default=True,
        help="Send email to requester when request is rejected"
    )

    # Activity settings
    create_activity = fields.Boolean(
        default=True,
        help="Create an activity for pending approvals"
    )
    activity_type_id = fields.Many2one(
        "mail.activity.type",
        string="Activity Type",
        default=lambda self: self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
    )

    # Automation
    auto_approve_amount = fields.Float(
        help="Automatically approve if amount is below this threshold (0 = disabled)"
    )
    amount_field = fields.Char(
        default="amount_total",
        help="Field name containing the amount to check (e.g., amount_total)"
    )

    # Statistics
    request_count = fields.Integer(compute="_compute_request_count", string="Requests")

    @api.onchange("res_model_id")
    def _onchange_res_model_id(self):
        if self.res_model_id:
            self.res_model = self.res_model_id.model

    @api.depends()
    def _compute_request_count(self):
        Request = self.env["ipai.approval.request"]
        for rec in self:
            rec.request_count = Request.search_count([("type_id", "=", rec.id)])

    def get_approvers(self, request):
        """
        Get the list of users who can approve this request.

        Args:
            request: The approval request record

        Returns:
            recordset of res.users
        """
        self.ensure_one()
        approvers = self.env["res.users"]

        if self.approval_type == "user":
            approvers = self.approver_ids

        elif self.approval_type == "group":
            if self.approver_group_id:
                approvers = self.approver_group_id.users

        elif self.approval_type == "manager":
            # Get employee's manager chain
            employee = self.env["hr.employee"].search([
                ("user_id", "=", request.user_id.id)
            ], limit=1)
            if employee:
                current = employee
                for _ in range(self.manager_levels):
                    if current.parent_id and current.parent_id.user_id:
                        approvers |= current.parent_id.user_id
                        current = current.parent_id
                    else:
                        break

        return approvers.filtered(lambda u: u.active)

    def action_view_requests(self):
        """Open requests for this approval type."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Requests - {self.name}",
            "res_model": "ipai.approval.request",
            "view_mode": "tree,form",
            "domain": [("type_id", "=", self.id)],
            "context": {"default_type_id": self.id},
        }
