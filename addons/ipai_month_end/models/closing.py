from datetime import timedelta
from odoo import models, fields, api


class MonthEndClosing(models.Model):
    """Month-end closing period with generated tasks."""

    _name = "ipai.month.end.closing"
    _description = "Month-End Closing"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_date desc"

    name = fields.Char(
        required=True,
        tracking=True,
        help="e.g., '2024-01 January Close'",
    )
    period_date = fields.Date(
        required=True,
        tracking=True,
        help="Last day of the accounting period being closed",
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("review", "Under Review"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )

    # Computed scheduling
    last_workday = fields.Date(
        compute="_compute_last_workday",
        store=True,
        help="Last working day for close (excludes holidays/weekends)",
    )

    # Tasks
    task_ids = fields.One2many(
        "ipai.month.end.task",
        "closing_id",
        string="Tasks",
    )

    # Statistics
    total_tasks = fields.Integer(compute="_compute_progress", store=True)
    completed_tasks = fields.Integer(compute="_compute_progress", store=True)
    progress = fields.Float(compute="_compute_progress", store=True)
    overdue_tasks = fields.Integer(compute="_compute_overdue")

    @api.depends("period_date")
    def _compute_last_workday(self):
        for rec in self:
            if rec.period_date:
                rec.last_workday = rec._find_last_workday(rec.period_date)
            else:
                rec.last_workday = False

    def _find_last_workday(self, date):
        """Find last working day on or before the given date."""
        current = date
        while not self._is_workday(current):
            current -= timedelta(days=1)
        return current

    def _is_workday(self, date_obj):
        """Check if date is a working day (not weekend or PH holiday)."""
        if date_obj.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        holidays = self.env["ipai.ph.holiday"].search([("date", "=", date_obj)])
        return not holidays

    def _get_workday_offset(self, base_date, offset_days):
        """Calculate date with working day offset.

        Args:
            base_date: Reference date
            offset_days: Number of working days (negative = before)

        Returns:
            Date after applying offset
        """
        current = base_date
        days_counted = 0
        direction = -1 if offset_days < 0 else 1
        target = abs(offset_days)

        while days_counted < target:
            current += timedelta(days=direction)
            if self._is_workday(current):
                days_counted += 1

        return current

    @api.depends("task_ids.state")
    def _compute_progress(self):
        for rec in self:
            total = len(rec.task_ids)
            done = len(rec.task_ids.filtered(lambda t: t.state == "done"))
            rec.total_tasks = total
            rec.completed_tasks = done
            rec.progress = (done / total * 100) if total else 0

    def _compute_overdue(self):
        today = fields.Date.today()
        for rec in self:
            rec.overdue_tasks = len(
                rec.task_ids.filtered(
                    lambda t: t.state not in ["done", "cancelled"]
                    and t.prep_due_date
                    and t.prep_due_date < today
                )
            )

    def action_generate_tasks(self):
        """Generate tasks from templates for this closing period."""
        self.ensure_one()
        templates = self.env["ipai.month.end.task.template"].search(
            [("active", "=", True)]
        )

        for template in templates:
            # Calculate due dates
            prep_date = self._get_workday_offset(
                self.last_workday, template.prep_day_offset
            )
            review_date = self._get_workday_offset(
                self.last_workday, template.review_day_offset
            )
            approve_date = self._get_workday_offset(
                self.last_workday, template.approve_day_offset
            )

            self.env["ipai.month.end.task"].create(
                {
                    "closing_id": self.id,
                    "template_id": template.id,
                    "name": template.name,
                    "phase": template.phase,
                    "sequence": template.sequence,
                    "prep_user_id": template.prep_user_id.id,
                    "review_user_id": template.review_user_id.id,
                    "approve_user_id": template.approve_user_id.id,
                    "prep_due_date": prep_date,
                    "review_due_date": review_date,
                    "approve_due_date": approve_date,
                }
            )

        self.state = "in_progress"
        return True

    def action_release(self):
        """Release closing for task execution."""
        self.ensure_one()
        self.state = "in_progress"

    def action_close(self):
        """Mark closing as complete."""
        self.ensure_one()
        self.state = "closed"

    def action_cancel(self):
        """Cancel closing."""
        self.ensure_one()
        self.state = "cancelled"
