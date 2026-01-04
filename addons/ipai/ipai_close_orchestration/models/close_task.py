# -*- coding: utf-8 -*-
"""
Close Task

Individual close task with prep → review → approval workflow.
"""
import logging

from odoo.exceptions import UserError

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CloseTask(models.Model):
    """
    Close Task with workflow states.
    """

    _name = "close.task"
    _description = "Close Task"
    _order = "cycle_id desc, sequence, id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Core fields
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)

    # Relationships
    cycle_id = fields.Many2one(
        "close.cycle",
        string="Close Cycle",
        required=True,
        ondelete="cascade",
        index=True,
    )
    template_id = fields.Many2one(
        "close.task.template",
        string="Template",
    )
    category_id = fields.Many2one(
        "close.task.category",
        string="Category",
    )

    # External key for idempotency
    external_key = fields.Char(
        string="External Key",
        index=True,
    )

    # Assignees
    preparer_id = fields.Many2one(
        "res.users",
        string="Preparer",
        tracking=True,
    )
    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer",
        tracking=True,
    )
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
            ("prep", "Preparation"),
            ("review", "Review"),
            ("approval", "Approval"),
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

    # Checklist
    checklist_ids = fields.One2many(
        "close.task.checklist",
        "task_id",
        string="Checklist",
    )
    checklist_progress = fields.Float(
        string="Checklist Progress",
        compute="_compute_checklist_progress",
        store=True,
    )

    # Exceptions
    exception_ids = fields.One2many(
        "close.exception",
        "task_id",
        string="Exceptions",
    )
    has_open_exceptions = fields.Boolean(
        string="Has Open Exceptions",
        compute="_compute_has_open_exceptions",
    )

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="cycle_id.company_id",
        store=True,
    )

    # Bridge to A1
    a1_task_id = fields.Many2one(
        "a1.task",
        string="A1 Task",
        help="Source task from A1 Control Center",
    )

    notes = fields.Html(string="Notes")

    @api.depends("checklist_ids.is_done")
    def _compute_checklist_progress(self):
        for task in self:
            total = len(task.checklist_ids)
            done = len(task.checklist_ids.filtered("is_done"))
            task.checklist_progress = (done / total * 100) if total else 0

    @api.depends("exception_ids", "exception_ids.state")
    def _compute_has_open_exceptions(self):
        for task in self:
            task.has_open_exceptions = bool(
                task.exception_ids.filtered(
                    lambda e: e.state not in ("resolved", "closed")
                )
            )

    def action_start_prep(self):
        """Start preparation."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Task must be in Draft state to start preparation.")
        self.state = "prep"
        self.message_post(body=f"Preparation started by {self.env.user.name}")
        self._trigger_webhook("close.task.state_changed", {"new_state": "prep"})

    def action_submit_prep(self):
        """Submit for review."""
        self.ensure_one()
        if self.state != "prep":
            raise UserError("Task must be in Preparation state.")

        # Check required checklist items
        required_incomplete = self.checklist_ids.filtered(
            lambda c: c.is_required and not c.is_done
        )
        if required_incomplete:
            raise UserError("Complete all required checklist items first.")

        if self.has_open_exceptions:
            raise UserError("Resolve all exceptions before submitting.")

        self.write(
            {
                "state": "review",
                "prep_done_date": fields.Datetime.now(),
                "prep_done_by": self.env.user.id,
            }
        )
        self.message_post(body=f"Submitted for review by {self.env.user.name}")
        self._trigger_webhook("close.task.state_changed", {"new_state": "review"})

    def action_start_review(self):
        """Start review (alias for clarity)."""
        # Review starts automatically when prep is submitted
        pass

    def action_submit_review(self):
        """Submit for approval."""
        self.ensure_one()
        if self.state != "review":
            raise UserError("Task must be in Review state.")

        self.write(
            {
                "state": "approval",
                "review_done_date": fields.Datetime.now(),
                "review_done_by": self.env.user.id,
            }
        )
        self.message_post(body=f"Submitted for approval by {self.env.user.name}")
        self._trigger_webhook("close.task.state_changed", {"new_state": "approval"})

    def action_approve(self):
        """Approve and complete."""
        self.ensure_one()
        if self.state != "approval":
            raise UserError("Task must be in Approval state.")

        self.write(
            {
                "state": "done",
                "approval_done_date": fields.Datetime.now(),
                "approval_done_by": self.env.user.id,
            }
        )
        self.message_post(body=f"Approved by {self.env.user.name}")
        self._trigger_webhook("close.task.state_changed", {"new_state": "done"})

    def action_reject(self):
        """Reject and return to prep."""
        self.ensure_one()
        if self.state not in ("review", "approval"):
            raise UserError("Task must be in Review or Approval state to reject.")

        self.state = "prep"
        self.message_post(body=f"Rejected by {self.env.user.name}")
        self._trigger_webhook(
            "close.task.state_changed", {"new_state": "prep", "rejected": True}
        )

    def action_cancel(self):
        """Cancel task."""
        self.ensure_one()
        self.state = "cancelled"
        self.message_post(body=f"Cancelled by {self.env.user.name}")
        self._trigger_webhook("close.task.state_changed", {"new_state": "cancelled"})

    def action_create_exception(self):
        """Create an exception for this task."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Create Exception",
            "res_model": "close.exception",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_task_id": self.id,
                "default_cycle_id": self.cycle_id.id,
            },
        }

    def _trigger_webhook(self, event_type, payload=None):
        """Trigger webhook for task events."""
        cycle = self.cycle_id
        if not cycle.webhook_url:
            return

        import json

        import requests

        data = {
            "source": "odoo",
            "module": "ipai_close_orchestration",
            "event": event_type,
            "company_id": self.company_id.id,
            "cycle": {"id": cycle.id, "name": cycle.name},
            "task": {
                "id": self.id,
                "code": self.external_key,
                "name": self.name,
                "state": self.state,
            },
            "ts": fields.Datetime.now().isoformat(),
        }
        if payload:
            data.update(payload)

        try:
            requests.post(
                cycle.webhook_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
        except Exception as e:
            _logger.warning("Webhook failed for task %s: %s", self.name, e)

    @api.model
    def _cron_send_due_reminders(self):
        """Send reminders for tasks approaching deadlines."""
        today = fields.Date.today()

        # Tasks that should start prep today
        prep_due = self.search(
            [
                ("state", "=", "draft"),
                ("prep_deadline", "=", today),
            ]
        )
        for task in prep_due:
            task.message_post(
                body="Reminder: Preparation deadline is today!",
                subtype_xmlid="mail.mt_note",
            )
            if task.preparer_id:
                task.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=task.preparer_id.id,
                    summary="Task prep deadline today",
                )

        # Tasks in review with review deadline today
        review_due = self.search(
            [
                ("state", "=", "review"),
                ("review_deadline", "=", today),
            ]
        )
        for task in review_due:
            task.message_post(
                body="Reminder: Review deadline is today!",
                subtype_xmlid="mail.mt_note",
            )
            if task.reviewer_id:
                task.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=task.reviewer_id.id,
                    summary="Task review deadline today",
                )

        # Tasks in approval with approval deadline today
        approval_due = self.search(
            [
                ("state", "=", "approval"),
                ("approval_deadline", "=", today),
            ]
        )
        for task in approval_due:
            task.message_post(
                body="Reminder: Approval deadline is today!",
                subtype_xmlid="mail.mt_note",
            )
            if task.approver_id:
                task.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=task.approver_id.id,
                    summary="Task approval deadline today",
                )

        _logger.info(
            "Due reminders sent: %d prep, %d review, %d approval",
            len(prep_due),
            len(review_due),
            len(approval_due),
        )


class CloseTaskChecklist(models.Model):
    """
    Checklist item for a close task.
    """

    _name = "close.task.checklist"
    _description = "Close Task Checklist"
    _order = "sequence, id"

    task_id = fields.Many2one(
        "close.task",
        string="Task",
        required=True,
        ondelete="cascade",
        index=True,
    )
    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    is_required = fields.Boolean(string="Required", default=True)
    is_done = fields.Boolean(string="Done", default=False)
    instructions = fields.Text(string="Instructions")

    # Completion
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
