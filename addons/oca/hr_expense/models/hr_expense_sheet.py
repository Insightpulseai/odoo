# Copyright 2024 IPAI - InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrExpenseSheet(models.Model):
    """Expense Report (collection of expenses for approval)."""

    _name = "hr.expense.sheet"
    _description = "Expense Report"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(
        string="Expense Report Summary",
        required=True,
        tracking=True,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Manager",
        related="employee_id.parent_id.user_id",
        store=True,
    )
    expense_line_ids = fields.One2many(
        "hr.expense",
        "sheet_id",
        string="Expense Lines",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submit", "Submitted"),
            ("approve", "Approved"),
            ("post", "Posted"),
            ("done", "Paid"),
            ("cancel", "Refused"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="company_id.currency_id",
    )
    total_amount = fields.Monetary(
        string="Total Amount",
        compute="_compute_amount",
        store=True,
        currency_field="currency_id",
    )
    untaxed_amount = fields.Monetary(
        string="Untaxed Amount",
        compute="_compute_amount",
        store=True,
        currency_field="currency_id",
    )
    total_tax_amount = fields.Monetary(
        string="Total Tax",
        compute="_compute_amount",
        store=True,
        currency_field="currency_id",
    )
    expense_count = fields.Integer(
        string="Expense Count",
        compute="_compute_amount",
        store=True,
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Expense Journal",
        domain="[('type', '=', 'purchase')]",
    )
    account_move_id = fields.Many2one(
        "account.move",
        string="Journal Entry",
        readonly=True,
    )
    payment_mode = fields.Selection(
        selection=[
            ("own_account", "Employee (to reimburse)"),
            ("company_account", "Company"),
        ],
        string="Payment Mode",
        compute="_compute_payment_mode",
        store=True,
    )
    approval_date = fields.Datetime(
        string="Approval Date",
        readonly=True,
    )
    accounting_date = fields.Date(
        string="Accounting Date",
        help="Date used for accounting entries.",
    )

    @api.depends("expense_line_ids.total_amount", "expense_line_ids.untaxed_amount", "expense_line_ids.tax_amount")
    def _compute_amount(self):
        for sheet in self:
            sheet.total_amount = sum(sheet.expense_line_ids.mapped("total_amount"))
            sheet.untaxed_amount = sum(sheet.expense_line_ids.mapped("untaxed_amount"))
            sheet.total_tax_amount = sum(sheet.expense_line_ids.mapped("tax_amount"))
            sheet.expense_count = len(sheet.expense_line_ids)

    @api.depends("expense_line_ids.payment_mode")
    def _compute_payment_mode(self):
        for sheet in self:
            payment_modes = sheet.expense_line_ids.mapped("payment_mode")
            if payment_modes:
                sheet.payment_mode = payment_modes[0]
            else:
                sheet.payment_mode = "own_account"

    @api.constrains("expense_line_ids")
    def _check_expense_lines(self):
        for sheet in self:
            employees = sheet.expense_line_ids.mapped("employee_id")
            if len(employees) > 1:
                raise ValidationError(
                    _("All expenses must belong to the same employee.")
                )

    def action_submit_sheet(self):
        """Submit expense report for approval."""
        self.ensure_one()
        if not self.expense_line_ids:
            raise UserError(_("Please add at least one expense line."))
        self.write({"state": "submit"})
        self.expense_line_ids.write({"state": "reported"})
        self.activity_schedule(
            "mail.mail_activity_data_todo",
            user_id=self.user_id.id or self.env.user.id,
            summary=_("Expense Report to Approve"),
        )

    def action_approve_expense_sheets(self):
        """Approve expense report."""
        self.ensure_one()
        if self.state != "submit":
            raise UserError(_("Only submitted expense reports can be approved."))
        self.write({
            "state": "approve",
            "approval_date": fields.Datetime.now(),
        })
        self.expense_line_ids.write({"state": "approved"})
        self.activity_feedback(["mail.mail_activity_data_todo"])

    def action_refuse_expense_sheets(self):
        """Open refuse wizard."""
        self.ensure_one()
        return {
            "name": _("Refuse Expense"),
            "type": "ir.actions.act_window",
            "res_model": "hr.expense.refuse.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_sheet_id": self.id},
        }

    def action_sheet_move_create(self):
        """Create journal entry for approved expenses."""
        for sheet in self:
            if sheet.state != "approve":
                raise UserError(_("Only approved expenses can be posted."))
            if not sheet.journal_id:
                sheet.journal_id = self.env["account.journal"].search(
                    [("type", "=", "purchase"), ("company_id", "=", sheet.company_id.id)],
                    limit=1,
                )
            if not sheet.journal_id:
                raise UserError(_("Please configure an expense journal."))

            move_vals = sheet._prepare_move_values()
            move = self.env["account.move"].create(move_vals)
            sheet.write({
                "account_move_id": move.id,
                "state": "post",
            })
            sheet.expense_line_ids.write({"state": "done"})

    def _prepare_move_values(self):
        """Prepare journal entry values."""
        self.ensure_one()
        move_lines = []

        for expense in self.expense_line_ids:
            account = expense.account_id or expense._get_default_expense_account()
            if not account:
                raise UserError(
                    _("Please configure an expense account for product '%s'.") % expense.product_id.display_name
                )

            # Expense line
            move_lines.append((0, 0, {
                "name": expense.name,
                "account_id": account.id,
                "debit": expense.untaxed_amount if expense.untaxed_amount > 0 else 0.0,
                "credit": -expense.untaxed_amount if expense.untaxed_amount < 0 else 0.0,
                "analytic_distribution": expense.analytic_distribution,
                "partner_id": expense.employee_id.work_contact_id.id,
            }))

            # Tax lines
            for tax in expense.tax_ids:
                tax_amount = expense.tax_amount / len(expense.tax_ids) if expense.tax_ids else 0
                if tax_amount:
                    move_lines.append((0, 0, {
                        "name": tax.name,
                        "account_id": tax.invoice_repartition_line_ids.filtered(
                            lambda l: l.repartition_type == "tax"
                        ).account_id.id or account.id,
                        "debit": tax_amount if tax_amount > 0 else 0.0,
                        "credit": -tax_amount if tax_amount < 0 else 0.0,
                    }))

        # Payable line
        payable_account = self.employee_id.work_contact_id.property_account_payable_id
        if not payable_account:
            payable_account = self.env["account.account"].search(
                [("account_type", "=", "liability_payable"), ("company_id", "=", self.company_id.id)],
                limit=1,
            )
        move_lines.append((0, 0, {
            "name": self.name,
            "account_id": payable_account.id,
            "debit": 0.0,
            "credit": self.total_amount,
            "partner_id": self.employee_id.work_contact_id.id,
        }))

        return {
            "journal_id": self.journal_id.id,
            "date": self.accounting_date or fields.Date.today(),
            "ref": self.name,
            "line_ids": move_lines,
            "move_type": "entry",
        }

    def action_reset_expense_sheets(self):
        """Reset to draft."""
        self.write({"state": "draft"})
        self.expense_line_ids.write({"state": "draft"})

    def action_open_account_move(self):
        """Open related journal entry."""
        self.ensure_one()
        return {
            "name": _("Journal Entry"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": self.account_move_id.id,
            "view_mode": "form",
        }
