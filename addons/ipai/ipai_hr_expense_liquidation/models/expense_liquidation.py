# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrExpenseLiquidation(models.Model):
    _name = "hr.expense.liquidation"
    _description = "Expense Liquidation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default="New",
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
    )
    liquidation_type = fields.Selection(
        [
            ("cash_advance", "Cash Advance"),
            ("reimbursement", "Reimbursement"),
            ("petty_cash", "Petty Cash"),
        ],
        string="Type",
        default="reimbursement",
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("done", "Done"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    advance_amount = fields.Monetary(
        string="Advance Amount",
        currency_field="currency_id",
    )
    total_expenses = fields.Monetary(
        string="Total Expenses",
        compute="_compute_total_expenses",
        store=True,
        currency_field="currency_id",
    )
    balance = fields.Monetary(
        string="Balance",
        compute="_compute_total_expenses",
        store=True,
        currency_field="currency_id",
    )
    line_ids = fields.One2many(
        "hr.expense.liquidation.line",
        "liquidation_id",
        string="Expense Lines",
    )
    date_submit = fields.Date(string="Submit Date")
    date_approve = fields.Date(string="Approval Date")
    notes = fields.Html(string="Notes")

    @api.depends("line_ids.amount", "advance_amount")
    def _compute_total_expenses(self):
        for rec in self:
            rec.total_expenses = sum(rec.line_ids.mapped("amount"))
            rec.balance = rec.advance_amount - rec.total_expenses

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "hr.expense.liquidation"
                ) or "New"
        return super().create(vals_list)

    def action_submit(self):
        self.ensure_one()
        self.write({"state": "submitted", "date_submit": fields.Date.today()})

    def action_approve(self):
        self.ensure_one()
        self.write({"state": "approved", "date_approve": fields.Date.today()})

    def action_done(self):
        self.ensure_one()
        self.write({"state": "done"})

    def action_reject(self):
        self.ensure_one()
        self.write({"state": "rejected"})

    def action_cancel(self):
        self.ensure_one()
        self.write({"state": "cancelled"})

    def action_draft(self):
        self.ensure_one()
        self.write({"state": "draft"})


class HrExpenseLiquidationLine(models.Model):
    _name = "hr.expense.liquidation.line"
    _description = "Expense Liquidation Line"
    _order = "date desc, id desc"

    liquidation_id = fields.Many2one(
        "hr.expense.liquidation",
        string="Liquidation",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(string="Description", required=True)
    date = fields.Date(string="Date", required=True, default=fields.Date.today)
    category = fields.Selection(
        [
            ("meals", "Meals"),
            ("transport", "Transportation"),
            ("accommodation", "Accommodation"),
            ("supplies", "Supplies"),
            ("misc", "Miscellaneous"),
        ],
        string="Category",
        default="misc",
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="liquidation_id.currency_id",
    )
    receipt_attached = fields.Boolean(string="Receipt Attached", default=False)
    notes = fields.Text(string="Notes")
