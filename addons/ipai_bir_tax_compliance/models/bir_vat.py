from odoo import api, fields, models
from odoo.exceptions import UserError


class BirVatReturn(models.Model):
    """VAT Return (Forms 2550M, 2550Q)"""
    _name = "bir.vat.return"
    _description = "BIR VAT Return"
    _inherit = ["bir.tax.return"]

    # VAT Output (Sales)
    vatable_sales = fields.Monetary(
        string="Vatable Sales",
        currency_field="currency_id",
        help="Sales subject to 12% VAT",
    )
    zero_rated_sales = fields.Monetary(
        string="Zero-Rated Sales",
        currency_field="currency_id",
        help="Export sales and other zero-rated transactions",
    )
    exempt_sales = fields.Monetary(
        string="Exempt Sales",
        currency_field="currency_id",
        help="VAT-exempt sales",
    )
    total_sales = fields.Monetary(
        string="Total Sales",
        compute="_compute_total_sales",
        store=True,
        currency_field="currency_id",
    )
    output_vat = fields.Monetary(
        string="Output VAT",
        compute="_compute_output_vat",
        store=True,
        currency_field="currency_id",
        help="12% of vatable sales",
    )

    # VAT Input (Purchases)
    vatable_purchases = fields.Monetary(
        string="Vatable Purchases",
        currency_field="currency_id",
    )
    purchase_of_services = fields.Monetary(
        string="Purchase of Services",
        currency_field="currency_id",
    )
    importations = fields.Monetary(
        string="Importations",
        currency_field="currency_id",
    )
    total_input_vat = fields.Monetary(
        string="Total Input VAT",
        compute="_compute_total_input_vat",
        store=True,
        currency_field="currency_id",
    )

    # Net VAT
    excess_input_vat_previous = fields.Monetary(
        string="Excess Input VAT (Previous Period)",
        currency_field="currency_id",
    )
    net_vat_payable = fields.Monetary(
        string="Net VAT Payable",
        compute="_compute_net_vat",
        store=True,
        currency_field="currency_id",
    )
    excess_input_vat = fields.Monetary(
        string="Excess Input VAT",
        compute="_compute_net_vat",
        store=True,
        currency_field="currency_id",
    )

    @api.depends("vatable_sales", "zero_rated_sales", "exempt_sales")
    def _compute_total_sales(self):
        for rec in self:
            rec.total_sales = rec.vatable_sales + rec.zero_rated_sales + rec.exempt_sales

    @api.depends("vatable_sales")
    def _compute_output_vat(self):
        for rec in self:
            rec.output_vat = rec.vatable_sales * 0.12

    @api.depends("vatable_purchases", "purchase_of_services", "importations")
    def _compute_total_input_vat(self):
        for rec in self:
            total_purchases = (
                rec.vatable_purchases + rec.purchase_of_services + rec.importations
            )
            rec.total_input_vat = total_purchases * 0.12

    @api.depends("output_vat", "total_input_vat", "excess_input_vat_previous")
    def _compute_net_vat(self):
        for rec in self:
            total_credits = rec.total_input_vat + rec.excess_input_vat_previous
            net = rec.output_vat - total_credits
            if net > 0:
                rec.net_vat_payable = net
                rec.excess_input_vat = 0
            else:
                rec.net_vat_payable = 0
                rec.excess_input_vat = abs(net)
            # Update base fields
            rec.tax_base = rec.total_sales
            rec.tax_due = rec.output_vat
            rec.tax_credits = total_credits

    def action_compute(self):
        """Compute VAT from account.move records"""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Can only compute draft returns")

        # Get all invoices in the period
        domain = [
            ("company_id", "=", self.company_id.id),
            ("date", ">=", self.period_start),
            ("date", "<=", self.period_end),
            ("state", "=", "posted"),
        ]

        # Sales invoices (out_invoice, out_refund)
        sales_domain = domain + [("move_type", "in", ("out_invoice", "out_refund"))]
        sales = self.env["account.move"].search(sales_domain)

        vatable = zero_rated = exempt = 0.0
        for inv in sales:
            for line in inv.invoice_line_ids:
                # Check tax types on line
                tax_tags = line.tax_ids.mapped("tax_group_id.name")
                if "VAT 12%" in str(tax_tags) or any(t.amount == 12 for t in line.tax_ids):
                    vatable += line.price_subtotal
                elif any(t.amount == 0 for t in line.tax_ids):
                    zero_rated += line.price_subtotal
                else:
                    exempt += line.price_subtotal

        # Purchase invoices (in_invoice, in_refund)
        purchase_domain = domain + [("move_type", "in", ("in_invoice", "in_refund"))]
        purchases = self.env["account.move"].search(purchase_domain)

        vatable_purchases = 0.0
        for bill in purchases:
            for line in bill.invoice_line_ids:
                if any(t.amount == 12 for t in line.tax_ids):
                    vatable_purchases += line.price_subtotal

        self.write({
            "vatable_sales": vatable,
            "zero_rated_sales": zero_rated,
            "exempt_sales": exempt,
            "vatable_purchases": vatable_purchases,
            "state": "computed",
        })


class BirVatLine(models.Model):
    """VAT Return Line Items (Sales/Purchases list)"""
    _name = "bir.vat.line"
    _description = "BIR VAT Line"

    return_id = fields.Many2one(
        "bir.vat.return",
        string="VAT Return",
        required=True,
        ondelete="cascade",
    )
    line_type = fields.Selection([
        ("sales", "Sales"),
        ("purchases", "Purchases"),
    ], string="Type", required=True)
    partner_id = fields.Many2one("res.partner", string="Customer/Supplier")
    tin = fields.Char(related="partner_id.tin", string="TIN")
    invoice_id = fields.Many2one("account.move", string="Invoice/Bill")
    invoice_date = fields.Date(related="invoice_id.invoice_date", string="Date")
    amount_untaxed = fields.Monetary(string="Amount (Net)", currency_field="currency_id")
    vat_amount = fields.Monetary(string="VAT Amount", currency_field="currency_id")
    vat_category = fields.Selection([
        ("vatable", "Vatable (12%)"),
        ("zero_rated", "Zero-Rated (0%)"),
        ("exempt", "Exempt"),
    ], string="VAT Category")
    currency_id = fields.Many2one(
        "res.currency",
        related="return_id.currency_id",
    )
