# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrExpenseLiquidation(models.Model):
    """
    Expense Liquidation Model with Cash Advance Tracking

    Supports 3 liquidation types:
    - Cash Advance: Employee receives advance, liquidates with itemized expenses
    - Reimbursement: Employee pays out-of-pocket, submits for reimbursement
    - Petty Cash: Small purchases from petty cash fund

    Features:
    - Itemized expense lines with bucket categorization
    - Automatic bucket totals (Meals, Transportation, Misc)
    - Cash advance settlement calculations
    - Multi-currency support
    """

    _name = "hr.expense.liquidation"
    _description = "Expense Liquidation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        default=lambda self: _("New"),
        copy=False,
    )

    # Liquidation Type
    liquidation_type = fields.Selection(
        [
            ("cash_advance", "Cash Advance"),
            ("reimbursement", "Reimbursement"),
            ("petty_cash", "Petty Cash"),
        ],
        string="Liquidation Type",
        required=True,
        default="cash_advance",
        tracking=True,
        help="Cash Advance: Settle advance with expenses | "
             "Reimbursement: Reimburse out-of-pocket expenses | "
             "Petty Cash: Small purchases from petty cash fund"
    )

    # Employee Info
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True,
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    # Dates
    date = fields.Date(
        string="Liquidation Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    period_start = fields.Date(string="Period Start")
    period_end = fields.Date(string="Period End")
    liquidation_report_date = fields.Date(
        string="Date Prepared",
        default=fields.Date.context_today,
        help="Date the liquidation report was prepared (TBWA report header)",
    )

    # Currency
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    # Cash Advance (for cash_advance type)
    advance_amount = fields.Monetary(
        string="Advance Amount",
        currency_field="currency_id",
        tracking=True,
        help="Cash advance received by employee"
    )
    advance_reference = fields.Char(string="Advance Reference")
    advance_date = fields.Date(string="Advance Date")

    # Expense Lines
    line_ids = fields.One2many(
        "hr.expense.liquidation.line",
        "liquidation_id",
        string="Expense Lines",
        copy=True,
    )
    line_count = fields.Integer(compute="_compute_line_count", string="Line Count")

    # Bucket Totals
    total_meals = fields.Monetary(
        string="Meals & Entertainment",
        currency_field="currency_id",
        compute="_compute_bucket_totals",
        store=True,
        help="Total expenses for meals and entertainment"
    )
    total_transportation = fields.Monetary(
        string="Transportation & Travel",
        currency_field="currency_id",
        compute="_compute_bucket_totals",
        store=True,
        help="Total expenses for transportation and travel"
    )
    total_miscellaneous = fields.Monetary(
        string="Miscellaneous",
        currency_field="currency_id",
        compute="_compute_bucket_totals",
        store=True,
        help="Other miscellaneous expenses"
    )

    # Totals
    total_expenses = fields.Monetary(
        string="Total Expenses",
        currency_field="currency_id",
        compute="_compute_totals",
        store=True,
    )
    settlement_amount = fields.Monetary(
        string="Settlement Amount",
        currency_field="currency_id",
        compute="_compute_settlement",
        store=True,
        help="Positive: Return to company | Negative: Additional reimbursement to employee"
    )
    settlement_status = fields.Selection(
        [
            ("return", "Return to Company"),
            ("balanced", "Balanced"),
            ("reimburse", "Reimburse Employee"),
        ],
        string="Settlement Status",
        compute="_compute_settlement",
        store=True,
    )

    # Approval Workflow
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("settled", "Settled"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    approver_id = fields.Many2one(
        "res.users",
        string="Approver",
        tracking=True,
    )
    approval_date = fields.Datetime(string="Approval Date", readonly=True)

    # Notes
    description = fields.Text(string="Purpose/Description")
    notes = fields.Text(string="Internal Notes")

    @api.depends("line_ids")
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    @api.depends("line_ids.amount", "line_ids.bucket")
    def _compute_bucket_totals(self):
        for record in self:
            record.total_meals = sum(
                line.amount for line in record.line_ids if line.bucket == "meals"
            )
            record.total_transportation = sum(
                line.amount for line in record.line_ids if line.bucket == "transportation"
            )
            record.total_miscellaneous = sum(
                line.amount for line in record.line_ids if line.bucket == "miscellaneous"
            )

    @api.depends("line_ids.amount")
    def _compute_totals(self):
        for record in self:
            record.total_expenses = sum(record.line_ids.mapped("amount"))

    @api.depends("liquidation_type", "advance_amount", "total_expenses")
    def _compute_settlement(self):
        for record in self:
            if record.liquidation_type == "cash_advance":
                # Positive = Return | Negative = Additional reimbursement
                record.settlement_amount = record.advance_amount - record.total_expenses

                if record.settlement_amount > 0:
                    record.settlement_status = "return"
                elif record.settlement_amount < 0:
                    record.settlement_status = "reimburse"
                else:
                    record.settlement_status = "balanced"
            else:
                # Reimbursement or Petty Cash: no settlement, just total
                record.settlement_amount = 0.0
                record.settlement_status = "balanced"

    @api.constrains("employee_id", "company_id")
    def _check_linked_expenses_scope(self):
        """
        Guard against cross-entity drift: any hr.expense records that reference
        this liquidation must share the same employee and company.
        Called on create/write of employee_id or company_id.
        """
        for rec in self:
            linked = self.env["hr.expense"].search(
                [("cash_advance_liquidation_id", "=", rec.id)], limit=50
            )
            bad_emp = linked.filtered(lambda e: e.employee_id != rec.employee_id)
            if bad_emp:
                raise ValidationError(_(
                    "Expense(s) '%s' belong to a different employee "
                    "and cannot be linked to this liquidation (%s)."
                ) % (", ".join(bad_emp.mapped("name")), rec.employee_id.name))
            bad_company = linked.filtered(lambda e: e.company_id != rec.company_id)
            if bad_company:
                raise ValidationError(_(
                    "Expense(s) '%s' belong to a different company "
                    "and cannot be linked to this liquidation."
                ) % ", ".join(bad_company.mapped("name")))

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("hr.expense.liquidation") or _("New")
        return super().create(vals)

    def action_submit(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(_("Cannot submit liquidation without expense lines."))
        self.write({"state": "submitted"})

    def action_approve(self):
        self.ensure_one()
        self.write({
            "state": "approved",
            "approver_id": self.env.user.id,
            "approval_date": fields.Datetime.now(),
        })

    def action_settle(self):
        self.ensure_one()
        if self.state != "approved":
            raise ValidationError(_("Only approved liquidations can be settled."))
        self.write({"state": "settled"})

    def action_reject(self):
        self.ensure_one()
        self.write({"state": "rejected"})

    def action_reset_to_draft(self):
        self.ensure_one()
        self.write({"state": "draft"})

    def action_view_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Expense Lines"),
            "res_model": "hr.expense.liquidation.line",
            "view_mode": "tree,form",
            "domain": [("liquidation_id", "=", self.id)],
            "context": {"default_liquidation_id": self.id},
        }


class HrExpenseLiquidationLine(models.Model):
    """
    Individual expense line items with bucket categorization
    """

    _name = "hr.expense.liquidation.line"
    _description = "Expense Liquidation Line"
    _order = "date desc, id"

    liquidation_id = fields.Many2one(
        "hr.expense.liquidation",
        string="Liquidation",
        required=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        "res.company",
        related="liquidation_id.company_id",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="liquidation_id.currency_id",
        store=True,
    )

    # Line Details
    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
    )
    description = fields.Char(
        string="Description",
        required=True,
    )
    bucket = fields.Selection(
        [
            ("meals", "Meals & Entertainment"),
            ("transportation", "Transportation & Travel"),
            ("miscellaneous", "Miscellaneous"),
        ],
        string="Bucket",
        required=True,
        default="miscellaneous",
        help="Expense category for bucket totals"
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        required=True,
    )

    # Receipt Attachment
    receipt_ids = fields.Many2many(
        "ir.attachment",
        "expense_line_receipt_rel",
        "line_id",
        "attachment_id",
        string="Receipts",
        help="Attach receipt images/PDFs for this expense line"
    )
    receipt_count = fields.Integer(compute="_compute_receipt_count", string="Receipt Count")

    # Reference
    reference = fields.Char(string="Reference/OR Number")

    @api.depends("receipt_ids")
    def _compute_receipt_count(self):
        for record in self:
            record.receipt_count = len(record.receipt_ids)

    def action_view_receipts(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Receipts"),
            "res_model": "ir.attachment",
            "view_mode": "kanban,tree,form",
            "domain": [("id", "in", self.receipt_ids.ids)],
            "context": {"create": False},
        }
