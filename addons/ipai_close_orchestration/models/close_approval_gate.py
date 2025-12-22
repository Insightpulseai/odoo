from odoo import api, fields, models
from odoo.exceptions import UserError


class CloseApprovalGate(models.Model):
    """Approval gates for close cycle checkpoints."""

    _name = "close.approval.gate"
    _description = "Close Approval Gate"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "cycle_id, gate_level"

    name = fields.Char(required=True)
    cycle_id = fields.Many2one(
        "close.cycle", required=True, ondelete="cascade", index=True
    )

    # Gate configuration
    gate_level = fields.Integer(
        required=True, help="1=Review Gate, 2=Approval Gate, 3=Lock Gate"
    )
    gate_type = fields.Selection(
        [
            ("review", "Review Gate"),
            ("approval", "Approval Gate"),
            ("lock", "GL Lock Gate"),
        ],
        required=True,
    )

    # Approval requirements
    approver_role = fields.Selection(
        [
            ("rim", "RIM"),
            ("sfm", "SFM"),
            ("ckvc", "CKVC - Controller"),
            ("fd", "FD - Finance Director"),
        ],
        required=True,
    )
    approver_user_id = fields.Many2one("res.users")
    required_approvals = fields.Integer(default=1)

    # Prerequisites
    required_task_states = fields.Char(
        default="done", help="Comma-separated task states required before gate can pass"
    )
    min_completion_pct = fields.Float(
        default=100.0, help="Minimum task completion % before gate can pass"
    )
    block_on_exceptions = fields.Boolean(
        default=True, help="Block gate if open exceptions exist"
    )

    # Status
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("ready", "Ready for Approval"),
            ("approved", "Approved"),
            ("blocked", "Blocked"),
        ],
        default="pending",
        tracking=True,
    )

    # Approval tracking
    approved_by = fields.Many2one("res.users")
    approved_date = fields.Datetime()
    approval_notes = fields.Text()

    # Blocking info
    blocking_reason = fields.Text()
    blocking_tasks = fields.Many2many("close.task", string="Blocking Tasks")
    blocking_exceptions = fields.Many2many(
        "close.exception", string="Blocking Exceptions"
    )

    @api.depends("cycle_id.task_ids", "cycle_id.exception_ids")
    def _compute_readiness(self):
        """Check if gate is ready for approval."""
        for gate in self:
            blocking_tasks = gate.cycle_id.task_ids.filtered(
                lambda t: t.state not in gate.required_task_states.split(",")
            )

            blocking_exceptions = []
            if gate.block_on_exceptions:
                blocking_exceptions = gate.cycle_id.exception_ids.filtered(
                    lambda e: e.state not in ("resolved", "cancelled")
                )

            if blocking_tasks or blocking_exceptions:
                gate.state = "blocked"
                gate.blocking_tasks = [(6, 0, blocking_tasks.ids)]
                gate.blocking_exceptions = [(6, 0, [e.id for e in blocking_exceptions])]
                gate.blocking_reason = (
                    f"{len(blocking_tasks)} incomplete tasks, "
                    f"{len(blocking_exceptions)} open exceptions"
                )
            else:
                if gate.state == "blocked":
                    gate.state = "ready"
                gate.blocking_tasks = [(5, 0, 0)]
                gate.blocking_exceptions = [(5, 0, 0)]
                gate.blocking_reason = False

    def action_approve(self):
        """Approve the gate."""
        self.ensure_one()
        if self.state != "ready":
            raise UserError("Gate is not ready for approval")

        self.state = "approved"
        self.approved_by = self.env.user
        self.approved_date = fields.Datetime.now()
        self.message_post(body=f"Gate approved by {self.env.user.name}")

        # Update cycle state based on gate type
        if self.gate_type == "lock" and self.cycle_id.state == "closed":
            self.cycle_id.action_lock()

    def action_check_readiness(self):
        """Manually check if gate is ready."""
        self._compute_readiness()

    @api.model
    def _cron_check_gates(self):
        """Periodically check gate readiness for active cycles."""
        active_gates = self.search(
            [
                ("cycle_id.state", "in", ("open", "in_progress", "review", "approval")),
                ("state", "in", ("pending", "blocked")),
            ]
        )
        for gate in active_gates:
            gate._compute_readiness()

            # Notify if gate became ready
            if gate.state == "ready" and gate.approver_user_id:
                gate.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=gate.approver_user_id.id,
                    summary=f"Gate Ready: {gate.name}",
                    note="This approval gate is now ready for your approval.",
                )
