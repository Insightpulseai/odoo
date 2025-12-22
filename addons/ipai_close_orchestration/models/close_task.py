from odoo import api, fields, models
from odoo.exceptions import UserError


class CloseTaskTemplate(models.Model):
    """Template for recurring close tasks."""

    _name = "close.task.template"
    _description = "Close Task Template"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    category_id = fields.Many2one("close.task.category", required=True)
    description = fields.Text()

    # Period applicability
    period_type = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
        ],
        help="Leave empty for all period types",
    )

    # Default assignments
    default_prep_user_id = fields.Many2one("res.users")
    default_review_user_id = fields.Many2one("res.users")
    default_approve_user_id = fields.Many2one("res.users")

    # Timing (days offset from period end)
    prep_day_offset = fields.Integer(
        default=-4, help="Days from period end for prep due date (negative = before)"
    )
    review_day_offset = fields.Integer(
        default=-2, help="Days from period end for review due date"
    )
    approve_day_offset = fields.Integer(
        default=0, help="Days from period end for approval due date"
    )

    # GL integration
    gl_account_ids = fields.Many2many("account.account", string="Affected GL Accounts")
    creates_gl_entry = fields.Boolean(
        default=False, help="Does this task create GL entries?"
    )

    # Checklist
    checklist_ids = fields.One2many("close.task.template.checklist", "template_id")

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("template_code_unique", "unique(code)", "Template code must be unique"),
    ]


class CloseTaskTemplateChecklist(models.Model):
    """Checklist items for close task templates."""

    _name = "close.task.template.checklist"
    _description = "Close Task Template Checklist"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "close.task.template", required=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    required = fields.Boolean(default=True)
    evidence_type = fields.Selection(
        [
            ("document", "Document Upload"),
            ("screenshot", "Screenshot"),
            ("gl_entry", "GL Entry Reference"),
            ("sign_off", "Sign-off Confirmation"),
        ],
        default="document",
    )


class CloseTask(models.Model):
    """Individual close task instance for a cycle."""

    _name = "close.task"
    _description = "Close Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "cycle_id, sequence, id"

    name = fields.Char(required=True, tracking=True)
    cycle_id = fields.Many2one(
        "close.cycle", required=True, ondelete="cascade", index=True
    )
    template_id = fields.Many2one("close.task.template")
    category_id = fields.Many2one("close.task.category", tracking=True)
    sequence = fields.Integer(default=10)
    description = fields.Text()

    # 3-Stage Workflow State
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("prep", "In Preparation"),
            ("prep_done", "Prep Complete"),
            ("review", "Under Review"),
            ("review_done", "Review Complete"),
            ("approval", "Pending Approval"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )

    # RACI Assignments
    # Preparation
    prep_user_id = fields.Many2one("res.users", string="Preparer", tracking=True)
    prep_due_date = fields.Date(string="Prep Due", tracking=True)
    prep_done_date = fields.Datetime(string="Prep Completed")
    prep_notes = fields.Text()

    # Review
    review_user_id = fields.Many2one("res.users", string="Reviewer", tracking=True)
    review_due_date = fields.Date(string="Review Due", tracking=True)
    review_done_date = fields.Datetime(string="Review Completed")
    review_notes = fields.Text()
    review_result = fields.Selection(
        [
            ("approved", "Approved"),
            ("rejected", "Rejected - Needs Rework"),
        ]
    )

    # Approval
    approve_user_id = fields.Many2one("res.users", string="Approver", tracking=True)
    approve_due_date = fields.Date(string="Approval Due", tracking=True)
    approve_done_date = fields.Datetime(string="Approved")
    approve_notes = fields.Text()

    # GL Integration
    gl_entry_ids = fields.Many2many("account.move", string="GL Entries Created")
    gl_entry_count = fields.Integer(compute="_compute_gl_entry_count")

    # Checklist
    checklist_ids = fields.One2many("close.task.checklist", "task_id")
    checklist_done_pct = fields.Float(compute="_compute_checklist_pct")

    # Attachments
    attachment_ids = fields.Many2many("ir.attachment", string="Supporting Documents")

    # Exceptions
    exception_ids = fields.One2many("close.exception", "task_id")
    has_exceptions = fields.Boolean(compute="_compute_has_exceptions")

    # Timing
    is_overdue = fields.Boolean(compute="_compute_is_overdue")
    days_overdue = fields.Integer(compute="_compute_is_overdue")

    @api.depends("gl_entry_ids")
    def _compute_gl_entry_count(self):
        for task in self:
            task.gl_entry_count = len(task.gl_entry_ids)

    @api.depends("checklist_ids", "checklist_ids.is_done")
    def _compute_checklist_pct(self):
        for task in self:
            items = task.checklist_ids
            if items:
                done = len(items.filtered("is_done"))
                task.checklist_done_pct = done / len(items) * 100
            else:
                task.checklist_done_pct = 100.0

    @api.depends("exception_ids", "exception_ids.state")
    def _compute_has_exceptions(self):
        for task in self:
            task.has_exceptions = bool(
                task.exception_ids.filtered(
                    lambda e: e.state not in ("resolved", "cancelled")
                )
            )

    @api.depends("state", "prep_due_date", "review_due_date", "approve_due_date")
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for task in self:
            due_date = False
            if task.state in ("draft", "prep"):
                due_date = task.prep_due_date
            elif task.state in ("prep_done", "review"):
                due_date = task.review_due_date
            elif task.state in ("review_done", "approval"):
                due_date = task.approve_due_date

            if due_date and today > due_date:
                task.is_overdue = True
                task.days_overdue = (today - due_date).days
            else:
                task.is_overdue = False
                task.days_overdue = 0

    # Workflow Actions
    def action_start_prep(self):
        """Start preparation phase."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Can only start prep from draft state")
        self.state = "prep"
        self.message_post(body=f"Preparation started by {self.env.user.name}")

    def action_submit_prep(self):
        """Submit preparation for review."""
        self.ensure_one()
        if self.state != "prep":
            raise UserError("Task not in preparation phase")

        # Check required checklist items
        required_incomplete = self.checklist_ids.filtered(
            lambda c: c.required and not c.is_done
        )
        if required_incomplete:
            raise UserError(
                f"Complete required checklist items first: "
                f"{', '.join(required_incomplete.mapped('name'))}"
            )

        self.state = "prep_done"
        self.prep_done_date = fields.Datetime.now()
        self.message_post(body="Preparation submitted for review")

        # Notify reviewer
        if self.review_user_id:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=self.review_user_id.id,
                summary=f"Review: {self.name}",
                note="Task ready for your review",
            )

    def action_start_review(self):
        """Start review phase."""
        self.ensure_one()
        if self.state != "prep_done":
            raise UserError("Task not ready for review")
        self.state = "review"
        self.message_post(body=f"Review started by {self.env.user.name}")

    def action_approve_review(self):
        """Approve review and move to approval phase."""
        self.ensure_one()
        if self.state != "review":
            raise UserError("Task not under review")

        self.state = "review_done"
        self.review_done_date = fields.Datetime.now()
        self.review_result = "approved"
        self.message_post(body="Review approved, moving to final approval")

        # Notify approver
        if self.approve_user_id:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=self.approve_user_id.id,
                summary=f"Approve: {self.name}",
                note="Task ready for final approval",
            )

    def action_reject_review(self):
        """Reject review and return to preparation."""
        self.ensure_one()
        if self.state != "review":
            raise UserError("Task not under review")

        self.state = "prep"
        self.review_result = "rejected"
        self.message_post(body=f"Review rejected: {self.review_notes or 'See notes'}")

        # Notify preparer
        if self.prep_user_id:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=self.prep_user_id.id,
                summary=f"Rework: {self.name}",
                note=f"Review rejected: {self.review_notes}",
            )

    def action_start_approval(self):
        """Start final approval phase."""
        self.ensure_one()
        if self.state != "review_done":
            raise UserError("Task not ready for approval")
        self.state = "approval"
        self.message_post(body=f"Final approval started by {self.env.user.name}")

    def action_final_approve(self):
        """Final approval - complete task."""
        self.ensure_one()
        if self.state != "approval":
            raise UserError("Task not in approval phase")

        self.state = "done"
        self.approve_done_date = fields.Datetime.now()
        self.message_post(body=f"Task approved and completed by {self.env.user.name}")

    def action_cancel(self):
        """Cancel task."""
        self.ensure_one()
        if self.state == "done":
            raise UserError("Cannot cancel completed tasks")
        self.state = "cancelled"
        self.message_post(body="Task cancelled")


class CloseTaskChecklist(models.Model):
    """Checklist items for a close task instance."""

    _name = "close.task.checklist"
    _description = "Close Task Checklist Item"
    _order = "sequence, id"

    task_id = fields.Many2one("close.task", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    required = fields.Boolean(default=True)
    evidence_type = fields.Selection(
        [
            ("document", "Document Upload"),
            ("screenshot", "Screenshot"),
            ("gl_entry", "GL Entry Reference"),
            ("sign_off", "Sign-off Confirmation"),
        ],
        default="document",
    )

    is_done = fields.Boolean(default=False)
    done_by = fields.Many2one("res.users")
    done_at = fields.Datetime()
    notes = fields.Text()
    attachment_id = fields.Many2one("ir.attachment")

    def action_mark_done(self):
        """Mark checklist item as done."""
        self.ensure_one()
        self.is_done = True
        self.done_by = self.env.user
        self.done_at = fields.Datetime.now()


class CloseTaskCron(models.Model):
    """Cron job methods for close tasks."""

    _inherit = "close.task"

    def action_view_gl_entries(self):
        """View GL entries for this task."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"GL Entries - {self.name}",
            "res_model": "account.move",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.gl_entry_ids.ids)],
        }

    @api.model
    def _cron_send_due_reminders(self):
        """Send reminders for tasks due soon or overdue."""
        from datetime import timedelta

        today = fields.Date.today()
        tomorrow = today + timedelta(days=1)

        # Find tasks due tomorrow
        tasks_due_tomorrow = self.search(
            [
                ("state", "not in", ("done", "cancelled")),
                "|",
                "|",
                ("prep_due_date", "=", tomorrow),
                ("review_due_date", "=", tomorrow),
                ("approve_due_date", "=", tomorrow),
            ]
        )

        for task in tasks_due_tomorrow:
            user_to_notify = False
            if task.state in ("draft", "prep") and task.prep_user_id:
                user_to_notify = task.prep_user_id
            elif task.state in ("prep_done", "review") and task.review_user_id:
                user_to_notify = task.review_user_id
            elif task.state in ("review_done", "approval") and task.approve_user_id:
                user_to_notify = task.approve_user_id

            if user_to_notify:
                task.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=user_to_notify.id,
                    summary=f"Due Tomorrow: {task.name}",
                    note="This task is due tomorrow. Please complete it promptly.",
                )

        # Find overdue tasks
        overdue_tasks = self.search(
            [
                ("state", "not in", ("done", "cancelled")),
                ("is_overdue", "=", True),
            ]
        )

        for task in overdue_tasks:
            task.message_post(
                body=f"OVERDUE: Task is {task.days_overdue} days overdue",
                message_type="notification",
            )
