from odoo import models, fields


class MonthEndTaskTemplate(models.Model):
    """Reusable month-end closing task templates."""

    _name = "ipai.month.end.task.template"
    _description = "Month-End Task Template"
    _order = "phase, sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    phase = fields.Selection(
        [
            ("I", "Phase I - Initial & Compliance"),
            ("II", "Phase II - Accruals & Amortization"),
            ("III", "Phase III - WIP"),
            ("IV", "Phase IV - Final Adjustments & Close"),
        ],
        required=True,
        default="I",
    )

    description = fields.Html("Description")

    # RACI Assignments (default users for generated tasks)
    prep_user_id = fields.Many2one(
        "res.users",
        string="Default Preparer",
        help="User responsible for preparing/executing the task",
    )
    review_user_id = fields.Many2one(
        "res.users",
        string="Default Reviewer",
        help="User responsible for reviewing the work",
    )
    approve_user_id = fields.Many2one(
        "res.users",
        string="Default Approver",
        help="User with final approval authority",
    )

    # Scheduling
    prep_day_offset = fields.Integer(
        string="Prep Day Offset",
        default=-5,
        help="Working days before close date. Negative = before close. E.g., -6 means 6 working days before.",
    )
    review_day_offset = fields.Integer(
        string="Review Day Offset",
        default=-3,
        help="Working days before close date for review deadline.",
    )
    approve_day_offset = fields.Integer(
        string="Approve Day Offset",
        default=-1,
        help="Working days before close date for approval deadline.",
    )

    # Dependencies
    depends_on_ids = fields.Many2many(
        "ipai.month.end.task.template",
        "ipai_task_template_dependency_rel",
        "task_id",
        "depends_on_id",
        string="Depends On",
        help="Tasks that must be completed before this task can start",
    )

    # Integration
    odoo_model = fields.Char(
        string="Related Odoo Model",
        help="e.g., account.move, account.asset.asset",
    )
    oca_module = fields.Char(
        string="OCA Module",
        help="e.g., account_asset_management, account_cutoff_base",
    )

    # Statistics
    task_count = fields.Integer(
        compute="_compute_task_count",
        string="Task Count",
    )

    def _compute_task_count(self):
        for rec in self:
            rec.task_count = self.env["ipai.month.end.task"].search_count(
                [("template_id", "=", rec.id)]
            )
