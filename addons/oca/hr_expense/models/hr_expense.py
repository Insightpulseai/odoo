# Copyright 2024 IPAI - InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrExpense(models.Model):
    """Employee Expense with OCR pipeline support."""

    _name = "hr.expense"
    _description = "Employee Expense"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Description",
        required=True,
        tracking=True,
    )
    date = fields.Date(
        string="Expense Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Expense Type",
        domain="[('can_be_expensed', '=', True)]",
        required=True,
        tracking=True,
    )
    unit_amount = fields.Float(
        string="Unit Price",
        required=True,
        digits="Product Price",
        tracking=True,
    )
    quantity = fields.Float(
        string="Quantity",
        required=True,
        default=1.0,
        digits="Product Unit of Measure",
    )
    total_amount = fields.Monetary(
        string="Total",
        compute="_compute_total_amount",
        store=True,
        currency_field="currency_id",
    )
    untaxed_amount = fields.Monetary(
        string="Subtotal",
        compute="_compute_total_amount",
        store=True,
        currency_field="currency_id",
    )
    tax_amount = fields.Monetary(
        string="Tax Amount",
        compute="_compute_total_amount",
        store=True,
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    tax_ids = fields.Many2many(
        "account.tax",
        string="Taxes",
        domain="[('type_tax_use', '=', 'purchase')]",
    )
    account_id = fields.Many2one(
        "account.account",
        string="Account",
        domain="[('account_type', 'not in', ('asset_receivable', 'liability_payable'))]",
        help="The expense account.",
    )
    analytic_distribution = fields.Json(
        string="Analytic Distribution",
    )
    sheet_id = fields.Many2one(
        "hr.expense.sheet",
        string="Expense Report",
        ondelete="cascade",
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "To Submit"),
            ("reported", "Submitted"),
            ("approved", "Approved"),
            ("done", "Paid"),
            ("refused", "Refused"),
        ],
        string="Status",
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    payment_mode = fields.Selection(
        selection=[
            ("own_account", "Employee (to reimburse)"),
            ("company_account", "Company"),
        ],
        string="Paid By",
        default="own_account",
        required=True,
        tracking=True,
    )
    attachment_number = fields.Integer(
        string="Number of Attachments",
        compute="_compute_attachment_number",
    )
    reference = fields.Char(
        string="Bill Reference",
        help="Reference of the vendor bill (OR/SI number for BIR compliance).",
    )
    description = fields.Text(
        string="Notes",
    )

    # OCR Pipeline Fields
    ocr_status = fields.Selection(
        selection=[
            ("none", "No OCR"),
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("done", "Completed"),
            ("failed", "Failed"),
        ],
        string="OCR Status",
        default="none",
        tracking=True,
    )
    ocr_confidence = fields.Float(
        string="OCR Confidence",
        help="Confidence score from OCR extraction (0-100%).",
    )
    ocr_extracted_data = fields.Json(
        string="OCR Extracted Data",
        help="Raw JSON data extracted by OCR pipeline.",
    )
    vendor_name = fields.Char(
        string="Vendor Name",
        help="Vendor name extracted from receipt.",
    )
    vendor_tin = fields.Char(
        string="Vendor TIN",
        help="Tax Identification Number for BIR compliance.",
    )

    @api.depends("unit_amount", "quantity", "tax_ids", "currency_id")
    def _compute_total_amount(self):
        for expense in self:
            taxes = expense.tax_ids.compute_all(
                expense.unit_amount,
                expense.currency_id,
                expense.quantity,
                product=expense.product_id,
                partner=expense.employee_id.user_id.partner_id,
            )
            expense.untaxed_amount = taxes["total_excluded"]
            expense.tax_amount = taxes["total_included"] - taxes["total_excluded"]
            expense.total_amount = taxes["total_included"]

    def _compute_attachment_number(self):
        attachment_data = self.env["ir.attachment"].read_group(
            [("res_model", "=", "hr.expense"), ("res_id", "in", self.ids)],
            ["res_id"],
            ["res_id"],
        )
        attachment_dict = {data["res_id"]: data["res_id_count"] for data in attachment_data}
        for expense in self:
            expense.attachment_number = attachment_dict.get(expense.id, 0)

    def action_view_attachments(self):
        """Open attachments view."""
        self.ensure_one()
        return {
            "name": _("Attachments"),
            "type": "ir.actions.act_window",
            "res_model": "ir.attachment",
            "view_mode": "kanban,tree,form",
            "domain": [("res_model", "=", "hr.expense"), ("res_id", "=", self.id)],
            "context": {
                "default_res_model": "hr.expense",
                "default_res_id": self.id,
            },
        }

    def action_submit_expenses(self):
        """Submit expense to a new or existing expense report."""
        if any(expense.state != "draft" for expense in self):
            raise UserError(_("You can only submit draft expenses."))

        # Create expense sheet
        sheet_vals = {
            "name": _("Expense Report - %s") % fields.Date.today(),
            "employee_id": self[0].employee_id.id,
            "expense_line_ids": [(6, 0, self.ids)],
        }
        sheet = self.env["hr.expense.sheet"].create(sheet_vals)
        self.write({"state": "reported"})

        return {
            "name": _("Expense Report"),
            "type": "ir.actions.act_window",
            "res_model": "hr.expense.sheet",
            "res_id": sheet.id,
            "view_mode": "form",
        }

    def action_trigger_ocr(self):
        """Trigger OCR pipeline for receipt processing."""
        for expense in self:
            if expense.attachment_number == 0:
                raise UserError(_("Please attach a receipt before triggering OCR."))
            expense.ocr_status = "pending"
            # OCR processing would be handled by ipai_expense_ocr connector
            # via n8n workflow or direct API call

    def _get_default_expense_account(self):
        """Get default expense account from product or category."""
        self.ensure_one()
        if self.product_id:
            account = self.product_id.property_account_expense_id
            if not account:
                account = self.product_id.categ_id.property_account_expense_categ_id
            return account
        return False

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.unit_amount = self.product_id.standard_price
            self.tax_ids = self.product_id.supplier_taxes_id.filtered(
                lambda t: t.company_id == self.company_id
            )
            account = self._get_default_expense_account()
            if account:
                self.account_id = account
