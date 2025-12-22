from odoo import api, fields, models


class FinanceTaskTemplate(models.Model):
    """
    Unified template for all finance tasks:
    - Month-end closing tasks (36 internal tasks)
    - BIR compliance tasks (filing deadlines)
    """

    _name = "finance.task.template"
    _description = "Finance Task Template"
    _order = "task_type, phase, sequence"

    name = fields.Char(string="Task Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(default=True)

    # Task classification
    task_type = fields.Selection(
        [
            ("month_end", "Month-End Closing"),
            ("bir_filing", "BIR Filing"),
            ("compliance", "Compliance Check"),
        ],
        string="Task Type",
        required=True,
        default="month_end",
    )

    # Month-end specific
    phase = fields.Selection(
        [
            ("I", "Phase I - Initial & Compliance"),
            ("II", "Phase II - Accruals & Amortization"),
            ("III", "Phase III - WIP & Inventory"),
            ("IV", "Phase IV - Final Adjustments & Close"),
        ],
        string="Phase",
        help="Month-end closing phase",
    )

    # BIR specific
    bir_form_type = fields.Selection(
        [
            ("2550M", "2550M - Monthly VAT"),
            ("2550Q", "2550Q - Quarterly VAT"),
            ("1601C", "1601-C - Compensation WHT"),
            ("1601E", "1601-E - Expanded WHT"),
            ("1601F", "1601-F - Final WHT"),
            ("1604CF", "1604-CF - Annual Alphalist (Comp)"),
            ("1604E", "1604-E - Annual Alphalist (Exp)"),
            ("1700", "1700 - Annual ITR (Comp Only)"),
            ("1701", "1701 - Annual ITR (Self-Employed)"),
            ("1702", "1702 - Annual Corporate ITR"),
            ("2551M", "2551M - Monthly Percentage Tax"),
        ],
        string="BIR Form",
    )

    frequency = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
            ("per_transaction", "Per Transaction"),
        ],
        string="Frequency",
        default="monthly",
    )

    # RACI assignments (defaults)
    prep_user_id = fields.Many2one("res.users", string="Default Preparer")
    review_user_id = fields.Many2one("res.users", string="Default Reviewer")
    approve_user_id = fields.Many2one("res.users", string="Default Approver")

    # Scheduling (workday offsets from period end)
    prep_day_offset = fields.Integer(
        string="Prep Due (Workdays)",
        default=-5,
        help="Workdays before period end. Negative = before, 0 = on period end",
    )
    review_day_offset = fields.Integer(
        string="Review Due (Workdays)",
        default=-3,
    )
    approve_day_offset = fields.Integer(
        string="Approval Due (Workdays)",
        default=-1,
    )

    # BIR filing offset (days after period end)
    filing_day_offset = fields.Integer(
        string="Filing Due (Days After)",
        default=20,
        help="Calendar days after period end for BIR filing deadline",
    )

    # Dependencies
    depends_on_ids = fields.Many2many(
        "finance.task.template",
        "finance_task_template_dependency_rel",
        "task_id",
        "depends_on_id",
        string="Depends On",
    )

    # Integration
    odoo_model = fields.Char(
        string="Odoo Model",
        help="Related Odoo model (e.g., account.move, account.bank.statement)",
    )
    oca_module = fields.Char(
        string="OCA Module",
        help="OCA module that provides this functionality",
    )

    description = fields.Html(string="Description / Instructions")

    # Stats
    task_count = fields.Integer(
        string="Tasks Created",
        compute="_compute_task_count",
    )

    def _compute_task_count(self):
        for rec in self:
            rec.task_count = self.env["finance.task"].search_count(
                [("template_id", "=", rec.id)]
            )
