from odoo import api, fields, models


class MonthEndTask(models.Model):
    """Generated month-end closing task with RACI workflow."""

    _name = "ipai.month.end.task"
    _description = "Month-End Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "closing_id, phase, sequence, id"

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10)

    closing_id = fields.Many2one(
        "ipai.month.end.closing",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    template_id = fields.Many2one(
        "ipai.month.end.task.template",
        ondelete="set null",
    )

    phase = fields.Selection(
        [
            ("I", "Phase I - Initial & Compliance"),
            ("II", "Phase II - Accruals & Amortization"),
            ("III", "Phase III - WIP"),
            ("IV", "Phase IV - Final Adjustments & Close"),
        ],
        required=True,
        default="I",
        tracking=True,
    )

    # RACI Assignments
    prep_user_id = fields.Many2one(
        "res.users",
        string="Preparer",
        tracking=True,
    )
    review_user_id = fields.Many2one(
        "res.users",
        string="Reviewer",
        tracking=True,
    )
    approve_user_id = fields.Many2one(
        "res.users",
        string="Approver",
        tracking=True,
    )

    # Due Dates
    prep_due_date = fields.Date(string="Prep Due Date", tracking=True)
    review_due_date = fields.Date(string="Review Due Date")
    approve_due_date = fields.Date(string="Approve Due Date")

    # Completion Tracking
    prep_done = fields.Boolean(default=False, tracking=True)
    prep_done_date = fields.Datetime()
    prep_done_by = fields.Many2one("res.users")

    review_done = fields.Boolean(default=False, tracking=True)
    review_done_date = fields.Datetime()
    review_done_by = fields.Many2one("res.users")

    approve_done = fields.Boolean(default=False, tracking=True)
    approve_done_date = fields.Datetime()
    approve_done_by = fields.Many2one("res.users")

    # Computed State
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("review", "Under Review"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        compute="_compute_state",
        store=True,
        tracking=True,
    )

    # Overdue Tracking
    days_overdue = fields.Integer(compute="_compute_days_overdue")
    is_overdue = fields.Boolean(compute="_compute_days_overdue")

    # Notes
    notes = fields.Html("Notes")

    @api.depends("prep_done", "review_done", "approve_done")
    def _compute_state(self):
        for rec in self:
            if rec.approve_done:
                rec.state = "done"
            elif rec.review_done:
                rec.state = "review"
            elif rec.prep_done:
                rec.state = "in_progress"
            else:
                rec.state = "pending"

    @api.depends("prep_due_date", "state")
    def _compute_days_overdue(self):
        today = fields.Date.today()
        for rec in self:
            if rec.prep_due_date and rec.state not in ["done", "cancelled"]:
                delta = (today - rec.prep_due_date).days
                rec.days_overdue = max(0, delta)
                rec.is_overdue = delta > 0
            else:
                rec.days_overdue = 0
                rec.is_overdue = False

    def action_mark_prep_done(self):
        """Mark preparation as complete."""
        self.ensure_one()
        self.write(
            {
                "prep_done": True,
                "prep_done_date": fields.Datetime.now(),
                "prep_done_by": self.env.user.id,
            }
        )
        # Schedule activity for reviewer
        if self.review_user_id:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=self.review_user_id.id,
                summary=f"Review: {self.name}",
                note=f"Task prepared by {self.env.user.name}. Please review.",
            )

    def action_mark_review_done(self):
        """Mark review as complete."""
        self.ensure_one()
        self.write(
            {
                "review_done": True,
                "review_done_date": fields.Datetime.now(),
                "review_done_by": self.env.user.id,
            }
        )
        # Schedule activity for approver
        if self.approve_user_id:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=self.approve_user_id.id,
                summary=f"Approve: {self.name}",
                note=f"Task reviewed by {self.env.user.name}. Ready for approval.",
            )

    def action_mark_approve_done(self):
        """Mark approval as complete."""
        self.ensure_one()
        self.write(
            {
                "approve_done": True,
                "approve_done_date": fields.Datetime.now(),
                "approve_done_by": self.env.user.id,
            }
        )
        # Mark all activities done
        self.activity_ids.action_feedback(feedback="Task approved and complete.")

    def action_cancel(self):
        """Cancel the task."""
        self.ensure_one()
        self.state = "cancelled"

    @api.model
    def _cron_send_overdue_notifications(self):
        """Daily cron to notify about overdue tasks."""
        overdue = self.search(
            [
                ("state", "not in", ["done", "cancelled"]),
                ("prep_due_date", "<", fields.Date.today()),
            ]
        )
        for task in overdue:
            if task.prep_user_id:
                task.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=task.prep_user_id.id,
                    summary=f"OVERDUE: {task.name}",
                    note=f"This task is {task.days_overdue} days overdue.",
                )
