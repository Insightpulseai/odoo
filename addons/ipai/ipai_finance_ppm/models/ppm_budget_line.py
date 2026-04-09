"""PPM Budget Line — budget vs forecast vs actual per project per period.

Delta model: this capability is not available in CE or OCA project modules.
"""

from odoo import api, fields, models


class PPMBudgetLine(models.Model):
    _name = "ppm.budget.line"
    _description = "PPM Budget Line"
    _order = "project_id, period_start"

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        related="project_id.company_id",
        store=True,
    )
    analytic_account_id = fields.Many2one(
        related="project_id.account_id",
        store=True,
    )

    period_start = fields.Date(string="Period Start", required=True)
    period_end = fields.Date(string="Period End", required=True)
    period_label = fields.Char(
        string="Period",
        compute="_compute_period_label",
        store=True,
    )

    budget_amount = fields.Monetary(
        string="Budget",
        currency_field="currency_id",
    )
    forecast_amount = fields.Monetary(
        string="Forecast",
        currency_field="currency_id",
    )
    actual_amount = fields.Monetary(
        string="Actual",
        currency_field="currency_id",
    )
    variance = fields.Monetary(
        string="Variance (Budget - Actual)",
        currency_field="currency_id",
        compute="_compute_variance",
        store=True,
    )
    variance_pct = fields.Float(
        string="Variance %",
        digits=(6, 2),
        compute="_compute_variance",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    cost_type = fields.Selection(
        [
            ("capex", "CAPEX"),
            ("opex", "OPEX"),
            ("mixed", "Mixed"),
        ],
        string="Cost Type",
        default="opex",
    )
    notes = fields.Text(string="Notes")

    @api.depends("period_start")
    def _compute_period_label(self):
        for line in self:
            if line.period_start:
                line.period_label = line.period_start.strftime("%Y-%m")
            else:
                line.period_label = ""

    @api.depends("budget_amount", "actual_amount")
    def _compute_variance(self):
        for line in self:
            line.variance = line.budget_amount - line.actual_amount
            if line.budget_amount:
                line.variance_pct = (line.variance / line.budget_amount) * 100
            else:
                line.variance_pct = 0.0

    _sql_constraints = [
        (
            "unique_project_period",
            "UNIQUE(project_id, period_start, cost_type)",
            "Only one budget line per project per period per cost type.",
        ),
    ]
