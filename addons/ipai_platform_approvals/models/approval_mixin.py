from odoo import models, fields, api


class ApprovalMixin(models.AbstractModel):
    """
    Mixin class providing approval chain capabilities.

    Inherit this mixin (along with ipai.workflow.mixin) to gain:
    - Approver resolution based on roles
    - Approval request/approve/reject actions
    - Delegation support
    - Escalation tracking

    Usage:
        class MyModel(models.Model):
            _name = 'my.model'
            _inherit = ['ipai.workflow.mixin', 'ipai.approval.mixin']
    """

    _name = "ipai.approval.mixin"
    _description = "IPAI Approval Mixin"

    approval_requested = fields.Boolean(
        string="Approval Requested",
        default=False,
        copy=False,
        tracking=True,
    )

    approval_requested_date = fields.Datetime(
        string="Approval Requested Date",
        readonly=True,
        copy=False,
    )

    approval_requested_by = fields.Many2one(
        "res.users",
        string="Requested By",
        readonly=True,
        copy=False,
    )

    current_approver_id = fields.Many2one(
        "res.users",
        string="Current Approver",
        compute="_compute_current_approver",
        store=True,
    )

    approval_notes = fields.Text(
        string="Approval Notes",
        tracking=True,
    )

    @api.depends("approval_requested")
    def _compute_current_approver(self):
        """Compute current approver based on approval rules."""
        for record in self:
            if record.approval_requested:
                record.current_approver_id = record._get_next_approver()
            else:
                record.current_approver_id = False

    def _get_next_approver(self):
        """
        Override to implement approver resolution logic.

        Returns:
            res.users record or False
        """
        # Default: return the user's manager if available
        self.ensure_one()
        if hasattr(self, "user_id") and self.user_id:
            user = self.user_id
            if hasattr(user, "employee_id") and user.employee_id:
                employee = user.employee_id
                if hasattr(employee, "parent_id") and employee.parent_id:
                    return employee.parent_id.user_id
        return False

    def _get_approval_groups(self):
        """
        Override to define groups that can approve this record.

        Returns:
            list of res.groups XML IDs
        """
        return []

    def action_request_approval(self):
        """Request approval for this record."""
        self.ensure_one()
        self.write(
            {
                "approval_requested": True,
                "approval_requested_date": fields.Datetime.now(),
                "approval_requested_by": self.env.uid,
            }
        )

        # Transition workflow state if available
        if hasattr(self, "workflow_transition"):
            if self._can_transition_to("pending_approval"):
                self.workflow_transition("pending_approval", "Approval requested")

        # Notify approver
        approver = self.current_approver_id
        if approver and hasattr(self, "message_post"):
            self.message_post(
                body=f"Approval requested. Assigned to: {approver.name}",
                partner_ids=[approver.partner_id.id],
                message_type="notification",
            )

        return True

    def action_approve(self, notes=None):
        """Approve this record."""
        self.ensure_one()

        # Check permission
        if not self._can_approve():
            from odoo.exceptions import AccessError

            raise AccessError("You are not authorized to approve this record.")

        self.write(
            {
                "approval_requested": False,
                "approval_notes": notes or "",
            }
        )

        # Transition workflow state if available
        if hasattr(self, "workflow_transition"):
            if self._can_transition_to("approved"):
                self.workflow_transition("approved", notes or "Approved")

        return True

    def action_reject(self, notes=None):
        """Reject this record."""
        self.ensure_one()

        # Check permission
        if not self._can_approve():
            from odoo.exceptions import AccessError

            raise AccessError("You are not authorized to reject this record.")

        self.write(
            {
                "approval_requested": False,
                "approval_notes": notes or "",
            }
        )

        # Transition workflow state if available
        if hasattr(self, "workflow_transition"):
            if self._can_transition_to("rejected"):
                self.workflow_transition("rejected", notes or "Rejected")

        return True

    def _can_approve(self):
        """Check if current user can approve/reject."""
        self.ensure_one()

        # Current approver can approve
        if self.current_approver_id == self.env.user:
            return True

        # Members of approval groups can approve
        for group_xmlid in self._get_approval_groups():
            if self.env.user.has_group(group_xmlid):
                return True

        return False
