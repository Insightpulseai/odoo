from odoo import fields, models


class PpmBudget(models.Model):
    _name = "ppm.budget"
    _description = "PPM Budget"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "fiscal_year desc"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    portfolio_id = fields.Many2one("ppm.portfolio", ondelete="cascade")
    program_id = fields.Many2one("ppm.program", ondelete="cascade")
    project_id = fields.Many2one("project.project", ondelete="cascade")
    fiscal_year = fields.Integer(required=True)

    approved_amount = fields.Float()
    forecast_amount = fields.Float()
    actual_amount = fields.Float()

    line_ids = fields.One2many("ppm.budget.line", "budget_id")


class PpmBudgetLine(models.Model):
    _name = "ppm.budget.line"
    _description = "PPM Budget Line"

    budget_id = fields.Many2one("ppm.budget", required=True, ondelete="cascade")
    category = fields.Selection(
        [
            ("labor", "Labor"),
            ("software", "Software"),
            ("vendor", "Vendor"),
            ("travel", "Travel"),
            ("other", "Other"),
        ],
        default="other",
    )
    description = fields.Text()
    amount = fields.Float(required=True)
    analytic_account_id = fields.Many2one("account.analytic.account")
