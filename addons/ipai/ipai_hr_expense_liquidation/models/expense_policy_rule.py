# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class HrExpensePolicyRule(models.Model):
    _name = "hr.expense.policy.rule"
    _description = "Expense Policy Rule"
    _order = "sequence, name"

    name = fields.Char(string="Rule Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    rule_type = fields.Selection(
        [
            ("amount_limit", "Amount Limit"),
            ("receipt_required", "Receipt Required"),
            ("category_limit", "Category Limit"),
        ],
        string="Rule Type",
        required=True,
    )
    amount_limit = fields.Float(string="Amount Limit")
    category = fields.Selection(
        [
            ("meals", "Meals"),
            ("transport", "Transportation"),
            ("accommodation", "Accommodation"),
            ("supplies", "Supplies"),
            ("misc", "Miscellaneous"),
        ],
        string="Category",
    )
    severity = fields.Selection(
        [
            ("warning", "Warning"),
            ("blocking", "Blocking"),
        ],
        string="Severity",
        default="warning",
    )
