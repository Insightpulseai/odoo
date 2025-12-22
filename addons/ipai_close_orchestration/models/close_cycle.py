from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class CloseCycle(models.Model):
    """Financial close cycle (monthly, quarterly, annual)."""

    _name = "close.cycle"
    _description = "Financial Close Cycle"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_end desc, id desc"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )

    # Period
    period_type = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
        ],
        default="monthly",
        required=True,
        tracking=True,
    )

    period_start = fields.Date(required=True, tracking=True)
    period_end = fields.Date(required=True, tracking=True)

    # Close timeline (Oct 24-29 pattern)
    close_start_date = fields.Date(
        string="Close Start", tracking=True, help="Day 1 of close cycle (e.g., Oct 24)"
    )
    close_target_date = fields.Date(
        string="Target Close",
        tracking=True,
        help="Target completion date (e.g., Oct 29)",
    )
    close_actual_date = fields.Date(string="Actual Close", tracking=True)

    # Status
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("review", "Under Review"),
            ("approval", "Pending Approval"),
            ("closed", "Closed"),
            ("locked", "Locked"),
        ],
        default="draft",
        tracking=True,
    )

    # Tasks
    task_ids = fields.One2many("close.task", "cycle_id", string="Close Tasks")
    task_count = fields.Integer(compute="_compute_task_stats", store=True)
    task_done_count = fields.Integer(compute="_compute_task_stats", store=True)
    task_completion_pct = fields.Float(
        compute="_compute_task_stats", store=True, string="Completion %"
    )

    # Exceptions
    exception_ids = fields.One2many("close.exception", "cycle_id")
    exception_count = fields.Integer(compute="_compute_exception_count")

    # Approval gates
    gate_ids = fields.One2many("close.approval.gate", "cycle_id")

    # Closing period link
    closing_period_id = fields.Many2one(
        "closing.period",
        string="Closing Period",
        help="Link to ipai_tbwa_finance closing period",
    )

    # KPIs
    cycle_time_days = fields.Integer(
        compute="_compute_cycle_time", string="Cycle Time (Days)"
    )

    @api.depends("task_ids", "task_ids.state")
    def _compute_task_stats(self):
        for cycle in self:
            tasks = cycle.task_ids
            cycle.task_count = len(tasks)
            cycle.task_done_count = len(tasks.filtered(lambda t: t.state == "done"))
            cycle.task_completion_pct = (
                (cycle.task_done_count / cycle.task_count * 100)
                if cycle.task_count
                else 0.0
            )

    @api.depends("exception_ids")
    def _compute_exception_count(self):
        for cycle in self:
            cycle.exception_count = len(
                cycle.exception_ids.filtered(
                    lambda e: e.state not in ("resolved", "cancelled")
                )
            )

    @api.depends("close_start_date", "close_actual_date")
    def _compute_cycle_time(self):
        for cycle in self:
            if cycle.close_start_date and cycle.close_actual_date:
                delta = cycle.close_actual_date - cycle.close_start_date
                cycle.cycle_time_days = delta.days + 1
            else:
                cycle.cycle_time_days = 0

    def action_open(self):
        """Open close cycle and generate tasks from templates."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Can only open draft cycles")

        self._generate_tasks_from_templates()
        self.state = "open"
        self.close_start_date = fields.Date.today()
        self.message_post(body="Close cycle opened. Tasks generated.")

    def action_start(self):
        """Start close cycle - move to in_progress."""
        self.ensure_one()
        self.state = "in_progress"
        self.message_post(body="Close cycle started.")

    def action_close(self):
        """Close the cycle after all tasks approved."""
        self.ensure_one()
        pending_tasks = self.task_ids.filtered(lambda t: t.state != "done")
        if pending_tasks:
            raise UserError(f"Cannot close: {len(pending_tasks)} tasks still pending")

        open_exceptions = self.exception_ids.filtered(
            lambda e: e.state not in ("resolved", "cancelled")
        )
        if open_exceptions:
            raise UserError(
                f"Cannot close: {len(open_exceptions)} unresolved exceptions"
            )

        self.state = "closed"
        self.close_actual_date = fields.Date.today()
        self.message_post(body="Close cycle completed successfully.")

    def action_lock(self):
        """Lock the cycle - no further changes allowed."""
        self.ensure_one()
        if self.state != "closed":
            raise UserError("Can only lock closed cycles")
        self.state = "locked"
        self.message_post(body="Close cycle locked. GL period sealed.")

    def _generate_tasks_from_templates(self):
        """Generate close tasks from active templates."""
        TaskTemplate = self.env["close.task.template"]
        templates = TaskTemplate.search(
            [
                ("active", "=", True),
                "|",
                ("period_type", "=", self.period_type),
                ("period_type", "=", False),
            ]
        )

        for tmpl in templates:
            self.env["close.task"].create(
                {
                    "cycle_id": self.id,
                    "template_id": tmpl.id,
                    "name": tmpl.name,
                    "category_id": tmpl.category_id.id,
                    "state": "draft",
                    "prep_user_id": tmpl.default_prep_user_id.id or False,
                    "review_user_id": tmpl.default_review_user_id.id or False,
                    "approve_user_id": tmpl.default_approve_user_id.id or False,
                    "prep_due_date": self._calculate_due_date(tmpl.prep_day_offset),
                    "review_due_date": self._calculate_due_date(tmpl.review_day_offset),
                    "approve_due_date": self._calculate_due_date(
                        tmpl.approve_day_offset
                    ),
                }
            )

    def _calculate_due_date(self, offset_days):
        """Calculate due date from period end with offset."""
        if not self.period_end:
            return False
        # Negative offset = before period end, positive = after
        return self.period_end + timedelta(days=offset_days)

    def action_view_tasks(self):
        """View tasks for this cycle."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Tasks - {self.name}",
            "res_model": "close.task",
            "view_mode": "kanban,tree,form",
            "domain": [("cycle_id", "=", self.id)],
            "context": {"default_cycle_id": self.id},
        }

    def action_view_exceptions(self):
        """View exceptions for this cycle."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Exceptions - {self.name}",
            "res_model": "close.exception",
            "view_mode": "kanban,tree,form",
            "domain": [("cycle_id", "=", self.id)],
            "context": {"default_cycle_id": self.id},
        }

    @api.model
    def _cron_daily_status(self):
        """Daily status check for active cycles."""
        active_cycles = self.search(
            [("state", "in", ("open", "in_progress", "review", "approval"))]
        )
        for cycle in active_cycles:
            # Calculate stats
            overdue_tasks = cycle.task_ids.filtered(lambda t: t.is_overdue)
            open_exceptions = cycle.exception_ids.filtered(
                lambda e: e.state not in ("resolved", "cancelled")
            )

            if overdue_tasks or open_exceptions:
                cycle.message_post(
                    body=f"Daily Status: {len(overdue_tasks)} overdue tasks, "
                    f"{len(open_exceptions)} open exceptions"
                )
