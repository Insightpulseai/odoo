from odoo import api, fields, models
from odoo.exceptions import UserError


class ClosingTaskList(models.Model):
    """Period instance of a closing template — e.g., 'Month-End Close - March 2026'."""

    _name = "closing.task.list"
    _description = "Closing Task List"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_end desc, id desc"

    name = fields.Char(required=True, tracking=True)
    template_id = fields.Many2one("closing.template", tracking=True)

    closing_type = fields.Selection(
        related="template_id.closing_type", store=True, readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    period_start = fields.Date(required=True, tracking=True)
    period_end = fields.Date(required=True, tracking=True)

    # BIR-specific: the statutory filing deadline
    bir_deadline = fields.Date(
        help="Statutory BIR filing deadline (e.g., 20th of following month for 2550M)",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("review", "Under Review"),
            ("approval", "Pending Approval"),
            ("closed", "Closed"),
            ("canceled", "Canceled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    task_ids = fields.One2many("closing.task", "task_list_id", string="Tasks")

    # Computed progress
    progress = fields.Float(compute="_compute_progress", store=True)
    task_count = fields.Integer(compute="_compute_progress", store=True)
    completed_count = fields.Integer(compute="_compute_progress", store=True)
    overdue_count = fields.Integer(compute="_compute_overdue_count")

    @api.depends("task_ids.state")
    def _compute_progress(self):
        for rec in self:
            tasks = rec.task_ids
            total = len(tasks)
            completed = len(tasks.filtered(
                lambda t: t.state in ("completed", "approved")
            ))
            rec.task_count = total
            rec.completed_count = completed
            rec.progress = (completed / total * 100.0) if total else 0.0

    def _compute_overdue_count(self):
        today = fields.Date.today()
        for rec in self:
            rec.overdue_count = len(rec.task_ids.filtered(
                lambda t: t.planned_date
                and t.planned_date < today
                and t.state not in ("completed", "approved", "canceled")
            ))

    def action_start(self):
        """Transition from draft to in_progress."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Can only start a task list in Draft state.")
            rec.state = "in_progress"

    def action_close(self):
        """Close the task list. All tasks must be in a terminal state."""
        for rec in self:
            open_tasks = rec.task_ids.filtered(
                lambda t: t.state not in ("completed", "approved", "canceled")
            )
            if open_tasks:
                raise UserError(
                    f"{len(open_tasks)} task(s) still open. "
                    "Complete or cancel all tasks before closing."
                )
            rec.state = "closed"

    def action_cancel(self):
        for rec in self:
            rec.state = "canceled"

    def action_generate_tasks(self):
        """Generate closing.task records from the linked template."""
        self.ensure_one()
        if not self.template_id:
            raise UserError("No template linked. Select a template first.")
        if self.task_ids:
            raise UserError("Tasks already exist. Delete them before regenerating.")

        Task = self.env["closing.task"]
        code_to_task = {}

        for line in self.template_id.line_ids.sorted("sequence"):
            # Compute planned date from reference + offset
            if line.deadline_reference == "bir_deadline" and self.bir_deadline:
                ref_date = self.bir_deadline
            else:
                ref_date = self.period_end

            planned_date = fields.Date.add(ref_date, days=line.deadline_offset_days) if ref_date else False

            task = Task.create({
                "name": line.name,
                "code": line.code,
                "template_line_id": line.id,
                "task_list_id": self.id,
                "task_type": line.task_type,
                "stage": line.stage,
                "planned_date": planned_date,
                "processor_role": line.processor_role,
                "responsible_role": line.responsible_role,
                "planned_hours": line.planned_hours,
                "description": line.description,
            })
            if line.code:
                code_to_task[line.code] = task

        # Wire up dependencies after all tasks exist
        for line in self.template_id.line_ids:
            if line.dependency_codes and line.code in code_to_task:
                task = code_to_task[line.code]
                dep_codes = [c.strip() for c in line.dependency_codes.split(",") if c.strip()]
                dep_tasks = [code_to_task[c] for c in dep_codes if c in code_to_task]
                if dep_tasks:
                    task.dependency_ids = [(6, 0, [t.id for t in dep_tasks])]

        self.state = "in_progress"
        return True

    def _check_auto_close(self):
        """SAP Tax Compliance cascade: when all tasks reach terminal state, auto-close the list."""
        for rec in self:
            if rec.state in ("closed", "canceled", "draft"):
                continue
            open_tasks = rec.task_ids.filtered(
                lambda t: t.state not in ("completed", "approved", "canceled")
            )
            if not open_tasks and rec.task_ids:
                rec.state = "closed"
                rec.message_post(
                    body="All tasks completed — task list auto-closed.",
                    message_type="notification",
                )
