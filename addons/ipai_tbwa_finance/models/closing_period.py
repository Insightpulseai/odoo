from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta


class ClosingPeriod(models.Model):
    """
    Represents a month-end closing period.
    Contains both internal closing tasks and BIR filing deadlines.
    """

    _name = "closing.period"
    _description = "Closing Period"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_date desc"

    name = fields.Char(
        string="Name",
        compute="_compute_name",
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    period_date = fields.Date(
        string="Period End Date",
        required=True,
        help="Last day of the accounting period (e.g., 2025-01-31)",
    )
    period_month = fields.Integer(
        string="Month",
        compute="_compute_period_parts",
        store=True,
    )
    period_year = fields.Integer(
        string="Year",
        compute="_compute_period_parts",
        store=True,
    )
    last_workday = fields.Date(
        string="Last Workday",
        compute="_compute_last_workday",
        store=True,
        help="Last working day of the period (excluding weekends/holidays)",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("review", "Under Review"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    # Task management
    task_ids = fields.One2many(
        "finance.task",
        "closing_id",
        string="Tasks",
    )
    total_tasks = fields.Integer(
        string="Total Tasks",
        compute="_compute_task_stats",
        store=True,
    )
    completed_tasks = fields.Integer(
        string="Completed",
        compute="_compute_task_stats",
        store=True,
    )
    progress = fields.Float(
        string="Progress %",
        compute="_compute_task_stats",
        store=True,
    )
    overdue_tasks = fields.Integer(
        string="Overdue",
        compute="_compute_task_stats",
        store=True,
    )

    # Separate counters by type
    month_end_tasks = fields.Integer(
        string="Month-End Tasks",
        compute="_compute_task_stats",
        store=True,
    )
    bir_tasks = fields.Integer(
        string="BIR Tasks",
        compute="_compute_task_stats",
        store=True,
    )

    notes = fields.Text(string="Notes")

    @api.depends("period_date")
    def _compute_name(self):
        for rec in self:
            if rec.period_date:
                rec.name = rec.period_date.strftime("%Y-%m %B")
            else:
                rec.name = "New Period"

    @api.depends("period_date")
    def _compute_period_parts(self):
        for rec in self:
            if rec.period_date:
                rec.period_month = rec.period_date.month
                rec.period_year = rec.period_date.year
            else:
                rec.period_month = 0
                rec.period_year = 0

    @api.depends("period_date", "company_id")
    def _compute_last_workday(self):
        Holiday = self.env["ph.holiday"]
        for rec in self:
            if rec.period_date:
                rec.last_workday = Holiday.get_last_workday_of_month(
                    rec.period_date.year,
                    rec.period_date.month,
                    rec.company_id.id if rec.company_id else None,
                )
            else:
                rec.last_workday = False

    @api.depends(
        "task_ids", "task_ids.state", "task_ids.is_overdue", "task_ids.task_type"
    )
    def _compute_task_stats(self):
        for rec in self:
            tasks = rec.task_ids
            rec.total_tasks = len(tasks)
            rec.completed_tasks = len(tasks.filtered(lambda t: t.state == "done"))
            rec.progress = (
                (rec.completed_tasks / rec.total_tasks * 100) if rec.total_tasks else 0
            )
            rec.overdue_tasks = len(tasks.filtered(lambda t: t.is_overdue))
            rec.month_end_tasks = len(
                tasks.filtered(lambda t: t.task_type == "month_end")
            )
            rec.bir_tasks = len(tasks.filtered(lambda t: t.task_type == "bir_filing"))

    def action_generate_tasks(self):
        """Generate all tasks from templates for this period"""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Can only generate tasks for draft periods")

        Holiday = self.env["ph.holiday"]
        templates = self.env["finance.task.template"].search([("active", "=", True)])

        for tmpl in templates:
            # Skip quarterly templates for non-quarter-end months
            if tmpl.frequency == "quarterly" and self.period_month not in [3, 6, 9, 12]:
                continue
            # Skip annual templates for non-December
            if tmpl.frequency == "annual" and self.period_month != 12:
                continue

            # Calculate due dates
            if tmpl.task_type == "month_end":
                prep_due = Holiday.get_workday_offset(
                    self.last_workday, tmpl.prep_day_offset, self.company_id.id
                )
                review_due = Holiday.get_workday_offset(
                    self.last_workday, tmpl.review_day_offset, self.company_id.id
                )
                approve_due = Holiday.get_workday_offset(
                    self.last_workday, tmpl.approve_day_offset, self.company_id.id
                )
                filing_due = False
            else:
                # BIR filing - days after period end
                prep_due = self.period_date + relativedelta(
                    days=tmpl.filing_day_offset - 5
                )
                review_due = self.period_date + relativedelta(
                    days=tmpl.filing_day_offset - 2
                )
                approve_due = self.period_date + relativedelta(
                    days=tmpl.filing_day_offset - 1
                )
                filing_due = self.period_date + relativedelta(
                    days=tmpl.filing_day_offset
                )

            self.env["finance.task"].create(
                {
                    "closing_id": self.id,
                    "template_id": tmpl.id,
                    "name": tmpl.name,
                    "task_type": tmpl.task_type,
                    "phase": tmpl.phase,
                    "bir_form_type": tmpl.bir_form_type,
                    "sequence": tmpl.sequence,
                    "prep_user_id": tmpl.prep_user_id.id,
                    "review_user_id": tmpl.review_user_id.id,
                    "approve_user_id": tmpl.approve_user_id.id,
                    "prep_due_date": prep_due,
                    "review_due_date": review_due,
                    "approve_due_date": approve_due,
                    "filing_due_date": filing_due,
                }
            )

        self.state = "open"
        return True

    def action_release(self):
        """Release period for work"""
        self.ensure_one()
        if self.state not in ("draft", "open"):
            raise UserError("Can only release draft or open periods")
        if not self.task_ids:
            raise UserError("Generate tasks first")
        self.state = "in_progress"

    def action_close(self):
        """Close the period"""
        self.ensure_one()
        incomplete = self.task_ids.filtered(lambda t: t.state != "done")
        if incomplete:
            raise UserError(f"Cannot close: {len(incomplete)} tasks incomplete")
        self.state = "closed"

    def action_cancel(self):
        """Cancel the period"""
        self.ensure_one()
        if self.state == "closed":
            raise UserError("Cannot cancel a closed period")
        self.state = "cancelled"
