from odoo import api, fields, models
from odoo.exceptions import UserError


class BirTaxReturn(models.Model):
    """Base model for all BIR tax returns"""

    _name = "bir.tax.return"
    _description = "BIR Tax Return"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_end desc, form_type"

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        default="New",
        copy=False,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    form_type = fields.Selection(
        [
            # VAT
            ("2550M", "2550M - Monthly VAT Declaration"),
            ("2550Q", "2550Q - Quarterly VAT Return"),
            # Withholding Tax
            ("1600", "1600 - Monthly VAT/Percentage Tax Withheld"),
            ("1601C", "1601-C - Monthly Compensation WHT"),
            ("1601E", "1601-E - Monthly Expanded WHT"),
            ("1601F", "1601-F - Monthly Final WHT"),
            ("1604CF", "1604-CF - Annual Compensation Alphalist"),
            ("1604E", "1604-E - Annual Expanded WHT Alphalist"),
            # Income Tax
            ("1700", "1700 - Annual Income Tax (Compensation Only)"),
            ("1701", "1701 - Annual Income Tax (Self-Employed)"),
            ("1701Q", "1701Q - Quarterly Income Tax"),
            ("1702RT", "1702-RT - Annual Corporate Tax (Regular)"),
            ("1702MX", "1702-MX - Annual Corporate Tax (Mixed)"),
            ("1702EX", "1702-EX - Annual Corporate Tax (Exempt)"),
            # Percentage Tax
            ("2551M", "2551M - Monthly Percentage Tax"),
            ("2551Q", "2551Q - Quarterly Percentage Tax"),
            # Excise Tax
            ("2200A", "2200A - Excise Tax (Alcohol)"),
            ("2200P", "2200P - Excise Tax (Petroleum)"),
            ("2200T", "2200T - Excise Tax (Tobacco)"),
            ("2200M", "2200M - Excise Tax (Minerals)"),
            ("2200AN", "2200AN - Excise Tax (Auto/Non-Essential)"),
            # Capital Gains
            ("1706", "1706 - Capital Gains Tax (Real Property)"),
            ("1707", "1707 - Capital Gains Tax (Shares)"),
            # Documentary Stamp
            ("2000", "2000 - Documentary Stamp Tax"),
            ("2000OT", "2000-OT - DST One-Time"),
            # Payment
            ("0605", "0605 - Payment Form"),
        ],
        string="Form Type",
        required=True,
        tracking=True,
    )

    tax_category = fields.Selection(
        [
            ("vat", "Value-Added Tax"),
            ("withholding", "Withholding Tax"),
            ("income", "Income Tax"),
            ("percentage", "Percentage Tax"),
            ("excise", "Excise Tax"),
            ("capital_gains", "Capital Gains Tax"),
            ("documentary_stamp", "Documentary Stamp Tax"),
            ("payment", "Payment"),
        ],
        string="Tax Category",
        compute="_compute_tax_category",
        store=True,
    )

    period_start = fields.Date(string="Period Start", required=True)
    period_end = fields.Date(string="Period End", required=True)
    frequency = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
            ("per_transaction", "Per Transaction"),
        ],
        string="Frequency",
        compute="_compute_frequency",
        store=True,
    )

    due_date = fields.Date(
        string="Filing Due Date",
        compute="_compute_due_date",
        store=True,
    )
    days_until_due = fields.Integer(
        string="Days Until Due",
        compute="_compute_days_until_due",
    )
    is_overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_days_until_due",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("computed", "Computed"),
            ("validated", "Validated"),
            ("filed", "Filed"),
            ("confirmed", "Confirmed by BIR"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    # Tax amounts
    tax_base = fields.Monetary(
        string="Tax Base",
        currency_field="currency_id",
    )
    tax_due = fields.Monetary(
        string="Tax Due",
        currency_field="currency_id",
    )
    tax_credits = fields.Monetary(
        string="Tax Credits",
        currency_field="currency_id",
    )
    tax_payable = fields.Monetary(
        string="Tax Payable",
        compute="_compute_tax_payable",
        store=True,
        currency_field="currency_id",
    )
    penalty = fields.Monetary(
        string="Penalty (if late)",
        currency_field="currency_id",
    )
    interest = fields.Monetary(
        string="Interest",
        currency_field="currency_id",
    )
    total_amount_due = fields.Monetary(
        string="Total Amount Due",
        compute="_compute_total_amount_due",
        store=True,
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    # Filing information
    filed_date = fields.Datetime(string="Filed Date", tracking=True)
    filed_by = fields.Many2one("res.users", string="Filed By")
    bir_reference = fields.Char(
        string="BIR Reference Number",
        help="Reference number from BIR after successful filing",
        tracking=True,
    )
    payment_date = fields.Date(string="Payment Date")
    payment_reference = fields.Char(string="Payment Reference")

    notes = fields.Text(string="Notes")
    line_ids = fields.One2many(
        "bir.tax.return.line",
        "return_id",
        string="Line Items",
    )

    @api.depends("form_type")
    def _compute_tax_category(self):
        category_map = {
            "2550M": "vat",
            "2550Q": "vat",
            "1600": "withholding",
            "1601C": "withholding",
            "1601E": "withholding",
            "1601F": "withholding",
            "1604CF": "withholding",
            "1604E": "withholding",
            "1700": "income",
            "1701": "income",
            "1701Q": "income",
            "1702RT": "income",
            "1702MX": "income",
            "1702EX": "income",
            "2551M": "percentage",
            "2551Q": "percentage",
            "2200A": "excise",
            "2200P": "excise",
            "2200T": "excise",
            "2200M": "excise",
            "2200AN": "excise",
            "1706": "capital_gains",
            "1707": "capital_gains",
            "2000": "documentary_stamp",
            "2000OT": "documentary_stamp",
            "0605": "payment",
        }
        for rec in self:
            rec.tax_category = category_map.get(rec.form_type, False)

    @api.depends("form_type")
    def _compute_frequency(self):
        frequency_map = {
            "2550M": "monthly",
            "2550Q": "quarterly",
            "1600": "monthly",
            "1601C": "monthly",
            "1601E": "monthly",
            "1601F": "monthly",
            "1604CF": "annual",
            "1604E": "annual",
            "1700": "annual",
            "1701": "annual",
            "1701Q": "quarterly",
            "1702RT": "annual",
            "1702MX": "annual",
            "1702EX": "annual",
            "2551M": "monthly",
            "2551Q": "quarterly",
            "2200A": "monthly",
            "2200P": "monthly",
            "2200T": "monthly",
            "2200M": "monthly",
            "2200AN": "monthly",
            "1706": "per_transaction",
            "1707": "per_transaction",
            "2000": "per_transaction",
            "2000OT": "per_transaction",
            "0605": "per_transaction",
        }
        for rec in self:
            rec.frequency = frequency_map.get(rec.form_type, "monthly")

    @api.depends("period_end", "form_type")
    def _compute_due_date(self):
        """Compute filing due date based on BIR rules"""
        from dateutil.relativedelta import relativedelta

        for rec in self:
            if not rec.period_end:
                rec.due_date = False
                continue
            # Most monthly forms: 20th of following month
            # Quarterly forms: 25th of month following quarter end
            # Annual forms: April 15 of following year
            if rec.frequency == "monthly":
                rec.due_date = rec.period_end + relativedelta(months=1, day=20)
            elif rec.frequency == "quarterly":
                rec.due_date = rec.period_end + relativedelta(months=1, day=25)
            elif rec.frequency == "annual":
                rec.due_date = rec.period_end + relativedelta(years=1, month=4, day=15)
            else:
                # Per transaction: 30 days
                rec.due_date = rec.period_end + relativedelta(days=30)

    @api.depends("due_date")
    def _compute_days_until_due(self):
        today = fields.Date.today()
        for rec in self:
            if rec.due_date:
                delta = (rec.due_date - today).days
                rec.days_until_due = delta
                rec.is_overdue = delta < 0 and rec.state not in (
                    "filed",
                    "confirmed",
                    "cancelled",
                )
            else:
                rec.days_until_due = 0
                rec.is_overdue = False

    @api.depends("tax_due", "tax_credits")
    def _compute_tax_payable(self):
        for rec in self:
            rec.tax_payable = rec.tax_due - rec.tax_credits

    @api.depends("tax_payable", "penalty", "interest")
    def _compute_total_amount_due(self):
        for rec in self:
            rec.total_amount_due = rec.tax_payable + rec.penalty + rec.interest

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                form_type = vals.get("form_type", "BIR")
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("bir.tax.return")
                    or f"BIR-{form_type}"
                )
        return super().create(vals_list)

    def action_compute(self):
        """Compute tax amounts from source documents"""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Can only compute draft returns")
        # Subclasses should override this method
        self.state = "computed"

    def action_validate(self):
        """Validate the return before filing"""
        self.ensure_one()
        if self.state not in ("draft", "computed"):
            raise UserError("Can only validate draft or computed returns")
        # TODO: Add validation rules
        self.state = "validated"

    def action_mark_filed(self):
        """Mark return as filed with BIR"""
        self.ensure_one()
        if self.state != "validated":
            raise UserError("Return must be validated before filing")
        self.write(
            {
                "state": "filed",
                "filed_date": fields.Datetime.now(),
                "filed_by": self.env.uid,
            }
        )

    def action_confirm(self):
        """Mark return as confirmed by BIR (reference number received)"""
        self.ensure_one()
        if self.state != "filed":
            raise UserError("Return must be filed before confirmation")
        if not self.bir_reference:
            raise UserError("BIR reference number is required for confirmation")
        self.state = "confirmed"

    def action_cancel(self):
        """Cancel the return"""
        self.ensure_one()
        if self.state == "confirmed":
            raise UserError("Cannot cancel a confirmed return")
        self.state = "cancelled"

    def action_reset_to_draft(self):
        """Reset to draft for corrections"""
        self.ensure_one()
        if self.state == "confirmed":
            raise UserError("Cannot reset a confirmed return")
        self.state = "draft"


class BirTaxReturnLine(models.Model):
    """Line items for BIR tax returns"""

    _name = "bir.tax.return.line"
    _description = "BIR Tax Return Line"
    _order = "sequence, id"

    return_id = fields.Many2one(
        "bir.tax.return",
        string="Tax Return",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Char(string="Description", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    tin = fields.Char(related="partner_id.tin", string="TIN")
    move_id = fields.Many2one("account.move", string="Source Document")
    tax_base = fields.Monetary(string="Tax Base", currency_field="currency_id")
    tax_rate = fields.Float(string="Tax Rate (%)")
    tax_amount = fields.Monetary(string="Tax Amount", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        related="return_id.currency_id",
    )
