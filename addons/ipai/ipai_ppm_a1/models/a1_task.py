# -*- coding: utf-8 -*-
"""
A1 Task

Individual task instance generated from a template for a specific period.
"""
from odoo import api, fields, models
from odoo.exceptions import UserError


class A1Task(models.Model):
    """
    Task instance for a specific period.

    Created from A1 Templates when a Tasklist (period run) is generated.
    """

    _name = "a1.task"
    _description = "A1 Task"
    _order = "tasklist_id desc, sequence, id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Core fields
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)

    # Relationships
    tasklist_id = fields.Many2one(
        "a1.tasklist",
        string="Tasklist",
        required=True,
        ondelete="cascade",
        index=True,
    )
    template_id = fields.Many2one(
        "a1.template",
        string="Template",
        help="Template this task was created from",
    )
    workstream_id = fields.Many2one(
        "a1.workstream",
        string="Workstream",
        related="template_id.workstream_id",
        store=True,
    )

    # External key for idempotency
    external_key = fields.Char(
        string="External Key",
        index=True,
        help="Deterministic key for idempotent upserts",
    )

    # Role assignments (resolved from template)
    owner_role = fields.Char(string="Owner Role")
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        tracking=True,
    )
    reviewer_role = fields.Char(string="Reviewer Role")
    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer",
        tracking=True,
    )
    approver_role = fields.Char(string="Approver Role")
    approver_id = fields.Many2one(
        "res.users",
        string="Approver",
        tracking=True,
    )

    # Deadlines
    prep_deadline = fields.Date(string="Prep Deadline")
    review_deadline = fields.Date(string="Review Deadline")
    approval_deadline = fields.Date(string="Approval Deadline")

    # Status
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("prep", "In Preparation"),
            ("review", "In Review"),
            ("approval", "Pending Approval"),
            ("done", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
        default="draft",
        tracking=True,
        required=True,
    )

    # Completion tracking
    prep_done_date = fields.Datetime(string="Prep Done At")
    prep_done_by = fields.Many2one("res.users", string="Prep Done By")
    review_done_date = fields.Datetime(string="Review Done At")
    review_done_by = fields.Many2one("res.users", string="Review Done By")
    approval_done_date = fields.Datetime(string="Approval Done At")
    approval_done_by = fields.Many2one("res.users", string="Approval Done By")

    # Checklist items
    checklist_ids = fields.One2many(
        "a1.task.checklist",
        "task_id",
        string="Checklist",
    )
    checklist_progress = fields.Float(
        string="Checklist Progress",
        compute="_compute_checklist_progress",
        store=True,
    )

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="tasklist_id.company_id",
        store=True,
    )

    # Bridge to close orchestration
    close_task_id = fields.Many2one(
        "close.task",
        string="Close Task",
        help="Linked task in Close Orchestration module",
    )

    # Notes
    notes = fields.Html(string="Notes")

    @api.depends("checklist_ids.is_done")
    def _compute_checklist_progress(self):
        for task in self:
            total = len(task.checklist_ids)
            done = len(task.checklist_ids.filtered("is_done"))
            task.checklist_progress = (done / total * 100) if total else 0

    def action_start_prep(self):
        """Start preparation phase."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Task must be in Draft state to start preparation.")
        self.state = "prep"
        self.message_post(body=f"Preparation started by {self.env.user.name}")

    def action_submit_prep(self):
        """Submit for review."""
        self.ensure_one()
        if self.state != "prep":
            raise UserError("Task must be in Preparation state to submit for review.")
        # Check required checklist items
        required_incomplete = self.checklist_ids.filtered(
            lambda c: c.is_required and not c.is_done
        )
        if required_incomplete:
            raise UserError("Complete all required checklist items before submitting.")

        self.write(
            {
                "state": "review",
                "prep_done_date": fields.Datetime.now(),
                "prep_done_by": self.env.user.id,
            }
        )
        self.message_post(body=f"Submitted for review by {self.env.user.name}")

    def action_submit_review(self):
        """Submit for approval."""
        self.ensure_one()
        if self.state != "review":
            raise UserError("Task must be in Review state to submit for approval.")

        self.write(
            {
                "state": "approval",
                "review_done_date": fields.Datetime.now(),
                "review_done_by": self.env.user.id,
            }
        )
        self.message_post(body=f"Submitted for approval by {self.env.user.name}")

    def action_approve(self):
        """Approve and complete task."""
        self.ensure_one()
        if self.state != "approval":
            raise UserError("Task must be in Pending Approval state to approve.")

        self.write(
            {
                "state": "done",
                "approval_done_date": fields.Datetime.now(),
                "approval_done_by": self.env.user.id,
            }
        )
        self.message_post(body=f"Approved by {self.env.user.name}")

    def action_reject(self):
        """Reject and return to preparation."""
        self.ensure_one()
        if self.state not in ("review", "approval"):
            raise UserError("Task must be in Review or Approval state to reject.")

        self.state = "prep"
        self.message_post(
            body=f"Rejected by {self.env.user.name} - returned to preparation"
        )

    def action_cancel(self):
        """Cancel task."""
        self.ensure_one()
        self.state = "cancelled"
        self.message_post(body=f"Cancelled by {self.env.user.name}")


class A1TaskChecklist(models.Model):
    """
    Checklist item instance for a task.
    """

    _name = "a1.task.checklist"
    _description = "A1 Task Checklist Item"
    _order = "sequence, id"

    task_id = fields.Many2one(
        "a1.task",
        string="Task",
        required=True,
        ondelete="cascade",
        index=True,
    )
    template_item_id = fields.Many2one(
        "a1.template.checklist",
        string="Template Item",
    )

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)

    item_type = fields.Selection(
        [
            ("check", "Checkbox"),
            ("input", "Input Value"),
            ("upload", "File Upload"),
            ("approve", "Approval Sign-off"),
        ],
        string="Type",
        default="check",
        required=True,
    )

    is_required = fields.Boolean(string="Required", default=True)
    is_done = fields.Boolean(string="Done", default=False)

    # Value storage
    value_text = fields.Text(string="Value")
    value_attachment_id = fields.Many2one("ir.attachment", string="Attachment")

    # Completion tracking
    done_date = fields.Datetime(string="Done At")
    done_by = fields.Many2one("res.users", string="Done By")

    def action_mark_done(self):
        """Mark item as done."""
        self.write(
            {
                "is_done": True,
                "done_date": fields.Datetime.now(),
                "done_by": self.env.user.id,
            }
        )
