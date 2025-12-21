# -*- coding: utf-8 -*-
"""
Close Cycle

Period-based closing run (maps from A1 Tasklist).
"""
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CloseCycle(models.Model):
    """
    Close Cycle representing a period's closing process.

    Bridged from A1 Tasklist.
    """

    _name = "close.cycle"
    _description = "Close Cycle"
    _order = "period_end desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _sql_constraints = [
        ("period_uniq", "unique(period_start, period_end, company_id)",
         "A cycle for this period already exists."),
    ]

    # Core fields
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )

    # Period
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
        string="Period",
        compute="_compute_period_label",
        store=True,
    )

    # Status
    state = fields.Selection([
        ("draft", "Draft"),
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("review", "Under Review"),
        ("closed", "Closed"),
        ("cancelled", "Cancelled"),
    ], string="State", default="draft", tracking=True, required=True)

    # Tasks
    task_ids = fields.One2many(
        "close.task",
        "cycle_id",
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

    # Exceptions
    exception_ids = fields.One2many(
        "close.exception",
        "cycle_id",
        string="Exceptions",
    )
    exception_count = fields.Integer(
        string="Exception Count",
        compute="_compute_exception_count",
    )
    open_exception_count = fields.Integer(
        string="Open Exceptions",
        compute="_compute_exception_count",
    )

    # Gates
    gate_ids = fields.One2many(
        "close.approval.gate",
        "cycle_id",
        string="Approval Gates",
    )
    gates_ready = fields.Boolean(
        string="All Gates Ready",
        compute="_compute_gates_ready",
    )

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # Bridge to A1
    a1_tasklist_id = fields.Many2one(
        "a1.tasklist",
        string="A1 Tasklist",
        help="Source tasklist from A1 Control Center",
    )

    # Webhook
    webhook_url = fields.Char(string="Webhook URL")

    notes = fields.Html(string="Notes")

    @api.depends("period_end")
    def _compute_period_label(self):
        for cycle in self:
            if cycle.period_end:
                cycle.period_label = cycle.period_end.strftime("%B %Y")
            else:
                cycle.period_label = ""

    @api.depends("task_ids", "task_ids.state")
    def _compute_task_stats(self):
        for cycle in self:
            tasks = cycle.task_ids
            cycle.task_count = len(tasks)
            cycle.task_done_count = len(tasks.filtered(lambda t: t.state == "done"))
            cycle.progress = (cycle.task_done_count / cycle.task_count * 100) if cycle.task_count else 0

    @api.depends("exception_ids", "exception_ids.state")
    def _compute_exception_count(self):
        for cycle in self:
            cycle.exception_count = len(cycle.exception_ids)
            cycle.open_exception_count = len(
                cycle.exception_ids.filtered(lambda e: e.state not in ("resolved", "closed"))
            )

    @api.depends("gate_ids", "gate_ids.state")
    def _compute_gates_ready(self):
        for cycle in self:
            if not cycle.gate_ids:
                cycle.gates_ready = True
            else:
                cycle.gates_ready = all(g.state == "passed" for g in cycle.gate_ids)

    def action_generate_tasks(self):
        """Generate close tasks from templates."""
        self.ensure_one()
        if self.state not in ("draft", "open"):
            raise UserError("Can only generate tasks for Draft or Open cycles.")

        templates = self.env["close.task.template"].search([
            ("active", "=", True),
            ("company_id", "=", self.company_id.id),
        ])

        created_count = 0
        for tpl in templates:
            # Check idempotency
            external_key = f"{self.period_label}|{tpl.code}"
            existing = self.env["close.task"].search([
                ("cycle_id", "=", self.id),
                ("external_key", "=", external_key),
            ], limit=1)

            if existing:
                continue

            # Calculate deadlines
            prep_deadline = self.period_end + timedelta(days=tpl.prep_offset)
            review_deadline = self.period_end + timedelta(days=tpl.review_offset)
            approval_deadline = self.period_end + timedelta(days=tpl.approval_offset)

            # Create task
            task = self.env["close.task"].create({
                "cycle_id": self.id,
                "template_id": tpl.id,
                "category_id": tpl.category_id.id if tpl.category_id else False,
                "name": tpl.name,
                "sequence": tpl.sequence,
                "external_key": external_key,
                "preparer_id": tpl.preparer_id.id if tpl.preparer_id else False,
                "reviewer_id": tpl.reviewer_id.id if tpl.reviewer_id else False,
                "approver_id": tpl.approver_id.id if tpl.approver_id else False,
                "prep_deadline": prep_deadline,
                "review_deadline": review_deadline,
                "approval_deadline": approval_deadline,
            })

            # Create checklist items
            for item in tpl.checklist_ids:
                self.env["close.task.checklist"].create({
                    "task_id": task.id,
                    "code": item.code,
                    "name": item.name,
                    "sequence": item.sequence,
                    "is_required": item.is_required,
                    "instructions": item.instructions,
                })

            created_count += 1

        self.state = "open"
        _logger.info("Generated %d tasks for close cycle %s", created_count, self.name)

        self._trigger_webhook("close.cycle.tasks_generated", {"task_count": created_count})

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Tasks Generated",
                "message": f"Created {created_count} close tasks.",
                "type": "success",
            },
        }

    def action_open(self):
        """Open the cycle."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Can only open Draft cycles.")
        self.state = "open"
        self._trigger_webhook("close.cycle.state_changed", {"new_state": "open"})

    def action_start(self):
        """Start the cycle."""
        self.ensure_one()
        if self.state != "open":
            raise UserError("Can only start Open cycles.")
        self.state = "in_progress"
        self._trigger_webhook("close.cycle.state_changed", {"new_state": "in_progress"})

    def action_submit_for_review(self):
        """Submit cycle for final review."""
        self.ensure_one()
        if self.state != "in_progress":
            raise UserError("Can only submit In Progress cycles for review.")

        incomplete = self.task_ids.filtered(lambda t: t.state not in ("done", "cancelled"))
        if incomplete:
            raise UserError(f"Cannot submit: {len(incomplete)} tasks not completed.")

        if not self.gates_ready:
            raise UserError("All approval gates must pass before submitting for review.")

        if self.open_exception_count > 0:
            raise UserError(f"Cannot submit: {self.open_exception_count} open exceptions.")

        self.state = "review"
        self._trigger_webhook("close.cycle.state_changed", {"new_state": "review"})

    def action_close(self):
        """Close the cycle."""
        self.ensure_one()
        if self.state != "review":
            raise UserError("Can only close cycles under review.")

        self.state = "closed"
        self._trigger_webhook("close.cycle.state_changed", {"new_state": "closed"})

    def action_view_tasks(self):
        """Open tasks for this cycle."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Tasks - {self.name}",
            "res_model": "close.task",
            "view_mode": "list,kanban,form",
            "domain": [("cycle_id", "=", self.id)],
            "context": {"default_cycle_id": self.id},
        }

    def action_view_exceptions(self):
        """Open exceptions for this cycle."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Exceptions - {self.name}",
            "res_model": "close.exception",
            "view_mode": "list,form",
            "domain": [("cycle_id", "=", self.id)],
            "context": {"default_cycle_id": self.id},
        }

    def _trigger_webhook(self, event_type, payload=None):
        """Trigger webhook for cycle events."""
        if not self.webhook_url:
            return

        import json
        import requests

        data = {
            "source": "odoo",
            "module": "ipai_close_orchestration",
            "event": event_type,
            "company_id": self.company_id.id,
            "cycle": {
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
            _logger.warning("Webhook failed for cycle %s: %s", self.name, e)
