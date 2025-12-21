from odoo import api, fields, models
from odoo.exceptions import UserError


class FinanceTask(models.Model):
    """
    Unified finance task model handling both:
    - Month-end closing tasks (internal)
    - BIR filing tasks (statutory)
    """
    _name = "finance.task"
    _description = "Finance Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "closing_id, task_type, phase, sequence"

    name = fields.Char(string="Task Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)

    closing_id = fields.Many2one(
        "closing.period",
        string="Closing Period",
        required=True,
        ondelete="cascade",
    )
    template_id = fields.Many2one(
        "finance.task.template",
        string="Template",
    )
    company_id = fields.Many2one(
        related="closing_id.company_id",
        store=True,
    )

    # Classification
    task_type = fields.Selection([
        ("month_end", "Month-End Closing"),
        ("bir_filing", "BIR Filing"),
        ("compliance", "Compliance Check"),
    ], string="Task Type", required=True, default="month_end")

    phase = fields.Selection([
        ("I", "Phase I - Initial"),
        ("II", "Phase II - Accruals"),
        ("III", "Phase III - WIP"),
        ("IV", "Phase IV - Close"),
    ], string="Phase")

    bir_form_type = fields.Selection([
        ("2550M", "2550M - Monthly VAT"),
        ("2550Q", "2550Q - Quarterly VAT"),
        ("1601C", "1601-C - Compensation WHT"),
        ("1601E", "1601-E - Expanded WHT"),
        ("1601F", "1601-F - Final WHT"),
        ("1604CF", "1604-CF - Alphalist (Comp)"),
        ("1604E", "1604-E - Alphalist (Exp)"),
        ("1700", "1700 - Annual ITR"),
        ("1702", "1702 - Corporate ITR"),
        ("2551M", "2551M - Percentage Tax"),
    ], string="BIR Form")

    # State machine (RACI workflow)
    state = fields.Selection([
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("review", "Under Review"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    ], string="Status", default="pending", tracking=True,
       compute="_compute_state", store=True, readonly=False)

    # RACI: Preparer
    prep_user_id = fields.Many2one("res.users", string="Preparer")
    prep_due_date = fields.Date(string="Prep Due Date")
    prep_done = fields.Boolean(string="Prep Done", tracking=True)
    prep_done_date = fields.Datetime(string="Prep Completed")
    prep_done_by = fields.Many2one("res.users", string="Prep By")

    # RACI: Reviewer
    review_user_id = fields.Many2one("res.users", string="Reviewer")
    review_due_date = fields.Date(string="Review Due Date")
    review_done = fields.Boolean(string="Review Done", tracking=True)
    review_done_date = fields.Datetime(string="Review Completed")
    review_done_by = fields.Many2one("res.users", string="Review By")

    # RACI: Approver
    approve_user_id = fields.Many2one("res.users", string="Approver")
    approve_due_date = fields.Date(string="Approval Due Date")
    approve_done = fields.Boolean(string="Approved", tracking=True)
    approve_done_date = fields.Datetime(string="Approval Date")
    approve_done_by = fields.Many2one("res.users", string="Approved By")

    # BIR Filing
    filing_due_date = fields.Date(string="BIR Filing Due")
    bir_reference = fields.Char(string="BIR Reference #")
    filed_date = fields.Datetime(string="Filed Date")

    # Overdue tracking
    is_overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_overdue",
        store=True,
    )
    days_overdue = fields.Integer(
        string="Days Overdue",
        compute="_compute_overdue",
        store=True,
    )

    # Linked documents
    bir_return_id = fields.Many2one("bir.return", string="BIR Return")
    notes = fields.Text(string="Notes")

    @api.depends("prep_done", "review_done", "approve_done")
    def _compute_state(self):
        for rec in self:
            if rec.state == "cancelled":
                continue
            if rec.approve_done:
                rec.state = "done"
            elif rec.review_done:
                rec.state = "review"
            elif rec.prep_done:
                rec.state = "in_progress"
            else:
                rec.state = "pending"

    @api.depends("prep_due_date", "state")
    def _compute_overdue(self):
        today = fields.Date.today()
        for rec in self:
            if rec.state in ("done", "cancelled"):
                rec.is_overdue = False
                rec.days_overdue = 0
            elif rec.prep_due_date and rec.prep_due_date < today:
                rec.is_overdue = True
                rec.days_overdue = (today - rec.prep_due_date).days
            else:
                rec.is_overdue = False
                rec.days_overdue = 0

    def action_mark_prep_done(self):
        """Mark preparation as done"""
        self.ensure_one()
        self.write({
            "prep_done": True,
            "prep_done_date": fields.Datetime.now(),
            "prep_done_by": self.env.uid,
        })

    def action_mark_review_done(self):
        """Mark review as done"""
        self.ensure_one()
        if not self.prep_done:
            raise UserError("Preparation must be completed first")
        self.write({
            "review_done": True,
            "review_done_date": fields.Datetime.now(),
            "review_done_by": self.env.uid,
        })

    def action_mark_approve_done(self):
        """Mark as approved"""
        self.ensure_one()
        if not self.review_done:
            raise UserError("Review must be completed first")
        self.write({
            "approve_done": True,
            "approve_done_date": fields.Datetime.now(),
            "approve_done_by": self.env.uid,
        })

    def action_cancel(self):
        """Cancel task"""
        self.ensure_one()
        self.state = "cancelled"

    def action_create_bir_return(self):
        """Create linked BIR return for filing tasks"""
        self.ensure_one()
        if self.task_type != "bir_filing":
            raise UserError("Only BIR filing tasks can create returns")
        if self.bir_return_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "bir.return",
                "res_id": self.bir_return_id.id,
                "view_mode": "form",
            }

        # Create new BIR return
        bir_return = self.env["bir.return"].create({
            "form_type": self.bir_form_type,
            "period_start": self.closing_id.period_date.replace(day=1),
            "period_end": self.closing_id.period_date,
            "company_id": self.company_id.id,
            "task_id": self.id,
        })
        self.bir_return_id = bir_return.id

        return {
            "type": "ir.actions.act_window",
            "res_model": "bir.return",
            "res_id": bir_return.id,
            "view_mode": "form",
        }

    @api.model
    def _cron_send_overdue_notifications(self):
        """Send notifications for overdue tasks"""
        overdue = self.search([
            ("is_overdue", "=", True),
            ("state", "not in", ("done", "cancelled")),
        ])
        for task in overdue:
            users = [task.prep_user_id, task.review_user_id, task.approve_user_id]
            for user in filter(None, users):
                task.activity_schedule(
                    "mail.mail_activity_data_warning",
                    user_id=user.id,
                    summary=f"Overdue: {task.name}",
                    note=f"Task is {task.days_overdue} days overdue",
                )
