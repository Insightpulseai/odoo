from odoo.exceptions import UserError

from odoo import api, fields, models


class BirReturn(models.Model):
    """
    BIR Tax Return - actual filing document.
    Linked to finance.task for workflow tracking.
    """

    _name = "bir.return"
    _description = "BIR Tax Return"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_end desc"

    name = fields.Char(
        string="Reference",
        compute="_compute_name",
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    task_id = fields.Many2one(
        "finance.task",
        string="Linked Task",
    )

    form_type = fields.Selection(
        [
            ("2550M", "2550M - Monthly VAT"),
            ("2550Q", "2550Q - Quarterly VAT"),
            ("1601C", "1601-C - Compensation WHT"),
            ("1601E", "1601-E - Expanded WHT"),
            ("1601F", "1601-F - Final WHT"),
            ("1604CF", "1604-CF - Alphalist"),
            ("1604E", "1604-E - Alphalist (Exp)"),
            ("1700", "1700 - Annual ITR"),
            ("1702", "1702 - Corporate ITR"),
            ("2551M", "2551M - Percentage Tax"),
        ],
        string="Form Type",
        required=True,
        tracking=True,
    )

    period_start = fields.Date(string="Period Start", required=True)
    period_end = fields.Date(string="Period End", required=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("computed", "Computed"),
            ("validated", "Validated"),
            ("filed", "Filed"),
            ("confirmed", "Confirmed"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    # Tax amounts
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )
    tax_base = fields.Monetary(string="Tax Base", currency_field="currency_id")
    tax_due = fields.Monetary(string="Tax Due", currency_field="currency_id")
    tax_credits = fields.Monetary(string="Tax Credits", currency_field="currency_id")
    tax_payable = fields.Monetary(
        string="Tax Payable",
        compute="_compute_tax_payable",
        store=True,
        currency_field="currency_id",
    )
    penalty = fields.Monetary(string="Penalty", currency_field="currency_id")
    interest = fields.Monetary(string="Interest", currency_field="currency_id")
    total_due = fields.Monetary(
        string="Total Due",
        compute="_compute_total_due",
        store=True,
        currency_field="currency_id",
    )

    # VAT specific
    vatable_sales = fields.Monetary(
        string="Vatable Sales", currency_field="currency_id"
    )
    zero_rated_sales = fields.Monetary(
        string="Zero-Rated Sales", currency_field="currency_id"
    )
    exempt_sales = fields.Monetary(string="Exempt Sales", currency_field="currency_id")
    output_vat = fields.Monetary(string="Output VAT", currency_field="currency_id")
    input_vat = fields.Monetary(string="Input VAT", currency_field="currency_id")

    # WHT specific
    total_payments = fields.Monetary(
        string="Total Payments", currency_field="currency_id"
    )
    total_wht = fields.Monetary(string="Total WHT", currency_field="currency_id")

    # Filing
    filed_date = fields.Datetime(string="Filed Date")
    filed_by = fields.Many2one("res.users", string="Filed By")
    bir_reference = fields.Char(string="BIR Reference #", tracking=True)
    payment_date = fields.Date(string="Payment Date")
    payment_reference = fields.Char(string="Payment Reference")

    line_ids = fields.One2many(
        "bir.return.line",
        "return_id",
        string="Details",
    )
    notes = fields.Text(string="Notes")

    @api.depends("form_type", "period_end")
    def _compute_name(self):
        for rec in self:
            if rec.form_type and rec.period_end:
                rec.name = f"{rec.form_type}-{rec.period_end.strftime('%Y%m')}"
            else:
                rec.name = "New"

    @api.depends("tax_due", "tax_credits")
    def _compute_tax_payable(self):
        for rec in self:
            rec.tax_payable = max(0, rec.tax_due - rec.tax_credits)

    @api.depends("tax_payable", "penalty", "interest")
    def _compute_total_due(self):
        for rec in self:
            rec.total_due = rec.tax_payable + rec.penalty + rec.interest

    def action_compute(self):
        """Compute tax from source documents"""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Can only compute draft returns")

        if self.form_type in ("2550M", "2550Q"):
            self._compute_vat()
        elif self.form_type in ("1601C", "1601E", "1601F"):
            self._compute_wht()

        self.state = "computed"

    def _compute_vat(self):
        """Compute VAT from invoices"""
        domain = [
            ("company_id", "=", self.company_id.id),
            ("date", ">=", self.period_start),
            ("date", "<=", self.period_end),
            ("state", "=", "posted"),
            ("move_type", "in", ("out_invoice", "out_refund")),
        ]
        invoices = self.env["account.move"].search(domain)

        vatable = zero = exempt = 0.0
        for inv in invoices:
            for line in inv.invoice_line_ids:
                if any(t.amount == 12 for t in line.tax_ids):
                    vatable += line.price_subtotal
                elif any(t.amount == 0 for t in line.tax_ids):
                    zero += line.price_subtotal
                else:
                    exempt += line.price_subtotal

        # Input VAT from purchases
        purchase_domain = [
            ("company_id", "=", self.company_id.id),
            ("date", ">=", self.period_start),
            ("date", "<=", self.period_end),
            ("state", "=", "posted"),
            ("move_type", "in", ("in_invoice", "in_refund")),
        ]
        bills = self.env["account.move"].search(purchase_domain)
        input_base = sum(
            line.price_subtotal
            for bill in bills
            for line in bill.invoice_line_ids
            if any(t.amount == 12 for t in line.tax_ids)
        )

        self.write(
            {
                "vatable_sales": vatable,
                "zero_rated_sales": zero,
                "exempt_sales": exempt,
                "output_vat": vatable * 0.12,
                "input_vat": input_base * 0.12,
                "tax_base": vatable + zero + exempt,
                "tax_due": vatable * 0.12,
                "tax_credits": input_base * 0.12,
            }
        )

    def _compute_wht(self):
        """Compute withholding tax"""
        # Placeholder - integrate with payroll
        self.write(
            {
                "tax_base": 0,
                "tax_due": 0,
            }
        )

    def action_validate(self):
        self.ensure_one()
        if self.state not in ("draft", "computed"):
            raise UserError("Can only validate draft/computed returns")
        self.state = "validated"

    def action_mark_filed(self):
        self.ensure_one()
        if self.state != "validated":
            raise UserError("Validate first")
        self.write(
            {
                "state": "filed",
                "filed_date": fields.Datetime.now(),
                "filed_by": self.env.uid,
            }
        )
        # Update linked task
        if self.task_id:
            self.task_id.action_mark_prep_done()

    def action_confirm(self):
        self.ensure_one()
        if self.state != "filed":
            raise UserError("Must be filed first")
        if not self.bir_reference:
            raise UserError("BIR Reference # required")
        self.state = "confirmed"
        if self.task_id:
            self.task_id.bir_reference = self.bir_reference
            self.task_id.filed_date = self.filed_date


class BirReturnLine(models.Model):
    """BIR Return Line Item"""

    _name = "bir.return.line"
    _description = "BIR Return Line"

    return_id = fields.Many2one(
        "bir.return",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one("res.partner", string="Partner")
    tin = fields.Char(related="partner_id.tin", string="TIN")
    description = fields.Char(string="Description")
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    tax_amount = fields.Monetary(string="Tax", currency_field="currency_id")
    move_id = fields.Many2one("account.move", string="Source Document")
    currency_id = fields.Many2one(related="return_id.currency_id")
