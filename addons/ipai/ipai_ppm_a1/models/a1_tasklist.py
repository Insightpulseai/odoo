# -*- coding: utf-8 -*-
"""
A1 Tasklist (Period Run)

Represents a period-specific instance of the task set.
Maps to close.cycle in the close orchestration module.
"""
import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class A1Tasklist(models.Model):
    """
    Tasklist representing a period run (e.g., December 2025 Month-End Close).

    When generated, creates A1 Tasks from all active templates.
    Can instantiate a close.cycle in the close orchestration module.
    """

    _name = "a1.tasklist"
    _description = "A1 Tasklist (Period Run)"
    _order = "period_end desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _sql_constraints = [
        (
            "period_uniq",
            "unique(period_start, period_end, company_id)",
            "A tasklist for this period already exists.",
        ),
    ]

    # Core fields
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )

    # Period definition
    period_start = fields.Date(
        string="Period Start",
        required=True,
        tracking=True,
    )
    period_end = fields.Date(
        string="Period End",
        required=True,
        tracking=True,
    )
    period_label = fields.Char(
        string="Period Label",
        compute="_compute_period_label",
        store=True,
    )

    # Status
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("done", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
        default="draft",
        tracking=True,
        required=True,
    )

    # Tasks
    task_ids = fields.One2many(
        "a1.task",
        "tasklist_id",
        string="Tasks",
    )
    task_count = fields.Integer(
        string="Task Count",
        compute="_compute_task_stats",
        store=True,
    )
    task_done_count = fields.Integer(
        string="Tasks Done",
        compute="_compute_task_stats",
        store=True,
    )
    progress = fields.Float(
        string="Progress",
        compute="_compute_task_stats",
        store=True,
    )

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # Bridge to close orchestration
    close_cycle_id = fields.Many2one(
        "close.cycle",
        string="Close Cycle",
        help="Linked cycle in Close Orchestration module",
    )

    # Webhook configuration
    webhook_url = fields.Char(
        string="Webhook URL",
        help="URL to call when tasklist events occur",
    )

    # Notes
    notes = fields.Html(string="Notes")

    @api.depends("period_start", "period_end")
    def _compute_period_label(self):
        for tl in self:
            if tl.period_end:
                tl.period_label = tl.period_end.strftime("%B %Y")
            else:
                tl.period_label = ""

    @api.depends("task_ids", "task_ids.state")
    def _compute_task_stats(self):
        for tl in self:
            tasks = tl.task_ids
            tl.task_count = len(tasks)
            tl.task_done_count = len(tasks.filtered(lambda t: t.state == "done"))
            tl.progress = (
                (tl.task_done_count / tl.task_count * 100) if tl.task_count else 0
            )

    def action_generate_tasks(self):
        """Generate tasks from all active templates."""
        self.ensure_one()
        if self.state not in ("draft", "open"):
            raise UserError("Can only generate tasks for Draft or Open tasklists.")

        templates = self.env["a1.template"].search(
            [
                ("active", "=", True),
                ("company_id", "=", self.company_id.id),
            ]
        )

        Role = self.env["a1.role"]
        created_count = 0

        for tpl in templates:
            # Check if task already exists (idempotency)
            external_key = f"{self.period_label}|{tpl.code}"
            existing = self.env["a1.task"].search(
                [
                    ("tasklist_id", "=", self.id),
                    ("external_key", "=", external_key),
                ],
                limit=1,
            )

            if existing:
                continue

            # Resolve roles to users
            owner = Role.resolve_user(tpl.owner_role, self.company_id.id)
            reviewer = Role.resolve_user(tpl.reviewer_role, self.company_id.id)
            approver = Role.resolve_user(tpl.approver_role, self.company_id.id)

            # Create task
            task = self.env["a1.task"].create(
                {
                    "tasklist_id": self.id,
                    "template_id": tpl.id,
                    "name": tpl.name,
                    "sequence": tpl.sequence,
                    "external_key": external_key,
                    "owner_role": tpl.owner_role,
                    "owner_id": owner.id if owner else False,
                    "reviewer_role": tpl.reviewer_role,
                    "reviewer_id": reviewer.id if reviewer else False,
                    "approver_role": tpl.approver_role,
                    "approver_id": approver.id if approver else False,
                    "prep_deadline": self.period_end,
                    "review_deadline": self.period_end,
                    "approval_deadline": self.period_end,
                }
            )

            # Create checklist items from template
            for item in tpl.checklist_ids:
                self.env["a1.task.checklist"].create(
                    {
                        "task_id": task.id,
                        "template_item_id": item.id,
                        "code": item.code,
                        "name": item.name,
                        "sequence": item.sequence,
                        "item_type": item.item_type,
                        "is_required": item.is_required,
                    }
                )

            created_count += 1

        self.state = "open"
        _logger.info("Generated %d tasks for tasklist %s", created_count, self.name)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Tasks Generated",
                "message": f"Created {created_count} tasks from templates.",
                "type": "success",
            },
        }

    def action_instantiate_close_cycle(self):
        """Create a close.cycle from this tasklist."""
        self.ensure_one()

        # Check if close orchestration module is installed
        if "close.cycle" not in self.env:
            raise UserError("Close Orchestration module not installed.")

        if self.close_cycle_id:
            raise UserError("Close cycle already exists for this tasklist.")

        # Create close cycle
        cycle = self.env["close.cycle"].create(
            {
                "name": self.name,
                "company_id": self.company_id.id,
                "period_start": self.period_start,
                "period_end": self.period_end,
                "a1_tasklist_id": self.id,
            }
        )

        self.close_cycle_id = cycle.id

        # Generate close tasks
        cycle.action_generate_tasks()

        return {
            "type": "ir.actions.act_window",
            "name": "Close Cycle",
            "res_model": "close.cycle",
            "res_id": cycle.id,
            "view_mode": "form",
        }

    def action_open(self):
        """Open the tasklist."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Can only open Draft tasklists.")
        self.state = "open"

    def action_start(self):
        """Start the tasklist (mark in progress)."""
        self.ensure_one()
        if self.state != "open":
            raise UserError("Can only start Open tasklists.")
        self.state = "in_progress"

    def action_complete(self):
        """Mark tasklist as complete."""
        self.ensure_one()
        if self.state != "in_progress":
            raise UserError("Can only complete In Progress tasklists.")

        incomplete = self.task_ids.filtered(
            lambda t: t.state not in ("done", "cancelled")
        )
        if incomplete:
            raise UserError(f"Cannot complete: {len(incomplete)} tasks not done.")

        self.state = "done"

    def action_view_tasks(self):
        """Open tasks for this tasklist."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Tasks - {self.name}",
            "res_model": "a1.task",
            "view_mode": "tree,form,kanban",
            "domain": [("tasklist_id", "=", self.id)],
            "context": {"default_tasklist_id": self.id},
        }

    def _trigger_webhook(self, event_type, payload=None):
        """Trigger webhook for tasklist events."""
        if not self.webhook_url:
            return

        import json
        import requests

        data = {
            "source": "odoo",
            "module": "ipai_ppm_a1",
            "event": event_type,
            "company_id": self.company_id.id,
            "tasklist": {
                "id": self.id,
                "name": self.name,
                "period": self.period_label,
                "state": self.state,
                "progress": self.progress,
            },
            "ts": fields.Datetime.now().isoformat(),
        }
        if payload:
            data.update(payload)

        try:
            requests.post(
                self.webhook_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
        except Exception as e:
            _logger.warning("Webhook failed for tasklist %s: %s", self.name, e)
