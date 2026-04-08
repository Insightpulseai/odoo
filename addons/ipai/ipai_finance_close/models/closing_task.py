from odoo import api, fields, models
from odoo.exceptions import UserError


class ClosingTask(models.Model):
    """Individual closing task within a task list."""

    _name = "closing.task"
    _description = "Closing Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "task_list_id, sequence, id"

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    template_line_id = fields.Many2one("closing.template.line", readonly=True)
    task_list_id = fields.Many2one(
        "closing.task.list", required=True, ondelete="cascade", index=True,
    )

    task_type = fields.Selection(
        [
            ("manual", "Manual"),
            ("automated", "Automated"),
            ("approval", "Approval"),
            ("checklist", "Checklist"),
        ],
        default="manual",
        required=True,
    )

    stage = fields.Selection(
        [
            ("preparation", "Preparation"),
            ("review", "Review"),
            ("approval", "Approval"),
            ("report_approval", "Report Approval"),
            ("payment_approval", "Payment Approval"),
            ("filing_payment", "Filing & Payment"),
        ],
        required=True,
        default="preparation",
    )

    # Status model (SAP-inspired: open → in_progress → completed/approved/failed/canceled)
    state = fields.Selection(
        [
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("completed_warning", "Completed with Warning"),
            ("completed_error", "Completed with Error"),
            ("failed", "Failed"),
            ("canceled", "Canceled"),
            ("approved", "Approved"),
        ],
        default="open",
        required=True,
        tracking=True,
    )

    state_changed_by = fields.Many2one("res.users", readonly=True)
    state_changed_date = fields.Datetime(readonly=True)
    completion_comment = fields.Text()

    # Scheduling
    planned_date = fields.Date(tracking=True)
    actual_start_date = fields.Datetime(readonly=True)
    actual_end_date = fields.Datetime(readonly=True)
    is_overdue = fields.Boolean(compute="_compute_is_overdue", store=True)

    # Assignment
    processor_id = fields.Many2one("hr.employee", string="Processor", tracking=True)
    processor_role = fields.Char(help="Role code from template, e.g., BOM")
    responsible_id = fields.Many2one("hr.employee", string="Responsible", tracking=True)
    responsible_role = fields.Char(help="Role code from template, e.g., RIM")

    # Dependencies
    dependency_ids = fields.Many2many(
        "closing.task",
        "closing_task_dependency_rel",
        "task_id",
        "dependency_id",
        string="Predecessors",
    )
    can_start = fields.Boolean(compute="_compute_can_start", store=True)

    planned_hours = fields.Float()
    description = fields.Text()
    company_id = fields.Many2one(related="task_list_id.company_id", store=True)

    @api.depends("planned_date", "state")
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_overdue = bool(
                rec.planned_date
                and rec.planned_date < today
                and rec.state not in ("completed", "approved", "canceled")
            )

    @api.depends("dependency_ids.state")
    def _compute_can_start(self):
        terminal = ("completed", "completed_warning", "completed_error", "approved", "canceled")
        for rec in self:
            if not rec.dependency_ids:
                rec.can_start = True
            else:
                rec.can_start = all(d.state in terminal for d in rec.dependency_ids)

    def action_start(self):
        for rec in self:
            if not rec.can_start:
                raise UserError(
                    f"Cannot start '{rec.name}' — predecessor tasks not yet completed."
                )
            rec.write({
                "state": "in_progress",
                "actual_start_date": fields.Datetime.now(),
                "state_changed_by": self.env.uid,
                "state_changed_date": fields.Datetime.now(),
            })

    def action_complete(self):
        for rec in self:
            rec.write({
                "state": "completed",
                "actual_end_date": fields.Datetime.now(),
                "state_changed_by": self.env.uid,
                "state_changed_date": fields.Datetime.now(),
            })
        self.mapped("task_list_id")._check_auto_close()

    def action_approve(self):
        for rec in self:
            rec.write({
                "state": "approved",
                "state_changed_by": self.env.uid,
                "state_changed_date": fields.Datetime.now(),
            })
        self.mapped("task_list_id")._check_auto_close()

    def action_fail(self):
        for rec in self:
            rec.write({
                "state": "failed",
                "state_changed_by": self.env.uid,
                "state_changed_date": fields.Datetime.now(),
            })

    def action_cancel(self):
        for rec in self:
            rec.write({
                "state": "canceled",
                "state_changed_by": self.env.uid,
                "state_changed_date": fields.Datetime.now(),
            })
        self.mapped("task_list_id")._check_auto_close()

    def write(self, vals):
        res = super().write(vals)
        if "state" in vals:
            self.mapped("task_list_id")._check_auto_close()
        return res
