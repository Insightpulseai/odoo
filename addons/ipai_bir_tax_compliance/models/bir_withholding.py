from odoo import api, fields, models
from odoo.exceptions import UserError


class BirWithholdingReturn(models.Model):
    """Withholding Tax Return (Forms 1600, 1601-C, 1601-E, 1601-F, 1604-CF)"""
    _name = "bir.withholding.return"
    _description = "BIR Withholding Tax Return"
    _inherit = ["bir.tax.return"]

    withholding_type = fields.Selection([
        ("compensation", "Compensation (1601-C)"),
        ("expanded", "Expanded (1601-E)"),
        ("final", "Final (1601-F)"),
        ("vat", "VAT/Percentage Withheld (1600)"),
    ], string="Withholding Type", required=True)

    # Compensation WHT (1601-C)
    total_compensation = fields.Monetary(
        string="Total Compensation",
        currency_field="currency_id",
    )
    taxable_compensation = fields.Monetary(
        string="Taxable Compensation",
        currency_field="currency_id",
    )
    compensation_tax_withheld = fields.Monetary(
        string="Tax Withheld on Compensation",
        currency_field="currency_id",
    )
    employee_count = fields.Integer(string="Number of Employees")

    # Expanded WHT (1601-E)
    total_payments = fields.Monetary(
        string="Total Payments to Payees",
        currency_field="currency_id",
    )
    expanded_wht_amount = fields.Monetary(
        string="Expanded WHT Amount",
        currency_field="currency_id",
    )

    # Final WHT (1601-F)
    final_wht_amount = fields.Monetary(
        string="Final WHT Amount",
        currency_field="currency_id",
    )

    line_ids = fields.One2many(
        "bir.withholding.line",
        "return_id",
        string="Payee Details",
    )

    @api.onchange("withholding_type")
    def _onchange_withholding_type(self):
        form_map = {
            "compensation": "1601C",
            "expanded": "1601E",
            "final": "1601F",
            "vat": "1600",
        }
        if self.withholding_type:
            self.form_type = form_map.get(self.withholding_type)

    def action_compute(self):
        """Compute withholding tax from payroll or vendor bills"""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Can only compute draft returns")

        if self.withholding_type == "compensation":
            self._compute_compensation_wht()
        elif self.withholding_type == "expanded":
            self._compute_expanded_wht()
        elif self.withholding_type == "final":
            self._compute_final_wht()

        self.state = "computed"

    def _compute_compensation_wht(self):
        """Compute withholding from payroll"""
        # Try to get from hr.payslip if hr_payroll is installed
        if "hr.payslip" not in self.env:
            return

        domain = [
            ("company_id", "=", self.company_id.id),
            ("date_from", ">=", self.period_start),
            ("date_to", "<=", self.period_end),
            ("state", "=", "done"),
        ]
        payslips = self.env["hr.payslip"].search(domain)

        total_comp = 0.0
        taxable_comp = 0.0
        tax_withheld = 0.0
        lines = []

        for slip in payslips:
            gross = sum(slip.line_ids.filtered(lambda l: l.category_id.code == "GROSS").mapped("total"))
            net = sum(slip.line_ids.filtered(lambda l: l.category_id.code == "NET").mapped("total"))
            # Tax withheld = Gross - Net - Deductions (simplified)
            wht = gross - net
            if wht > 0:
                total_comp += gross
                taxable_comp += gross  # Simplified
                tax_withheld += wht
                lines.append((0, 0, {
                    "partner_id": slip.employee_id.address_home_id.id if slip.employee_id.address_home_id else False,
                    "income_type": "compensation",
                    "gross_income": gross,
                    "wht_rate": 0,  # Progressive rate
                    "wht_amount": wht,
                    "payslip_id": slip.id,
                }))

        self.write({
            "total_compensation": total_comp,
            "taxable_compensation": taxable_comp,
            "compensation_tax_withheld": tax_withheld,
            "employee_count": len(payslips.mapped("employee_id")),
            "tax_base": taxable_comp,
            "tax_due": tax_withheld,
            "line_ids": [(5, 0, 0)] + lines,
        })

    def _compute_expanded_wht(self):
        """Compute expanded withholding from vendor bills"""
        domain = [
            ("company_id", "=", self.company_id.id),
            ("move_type", "=", "in_invoice"),
            ("invoice_date", ">=", self.period_start),
            ("invoice_date", "<=", self.period_end),
            ("state", "=", "posted"),
        ]
        bills = self.env["account.move"].search(domain)

        total = 0.0
        wht_total = 0.0
        lines = []

        for bill in bills:
            for line in bill.invoice_line_ids:
                # Check for EWT taxes (expanded withholding)
                ewt_taxes = line.tax_ids.filtered(lambda t: "EWT" in (t.name or "").upper() or t.amount < 0)
                if ewt_taxes:
                    wht = abs(sum(ewt_taxes.mapped("amount")) / 100 * line.price_subtotal)
                    total += line.price_subtotal
                    wht_total += wht
                    lines.append((0, 0, {
                        "partner_id": bill.partner_id.id,
                        "income_type": "professional_fees" if "professional" in line.name.lower() else "other",
                        "gross_income": line.price_subtotal,
                        "wht_rate": abs(sum(ewt_taxes.mapped("amount"))),
                        "wht_amount": wht,
                        "move_id": bill.id,
                    }))

        self.write({
            "total_payments": total,
            "expanded_wht_amount": wht_total,
            "tax_base": total,
            "tax_due": wht_total,
            "line_ids": [(5, 0, 0)] + lines,
        })

    def _compute_final_wht(self):
        """Compute final withholding (interest, dividends, etc.)"""
        # Similar logic for final withholding
        self.write({
            "tax_base": 0,
            "tax_due": 0,
        })


class BirWithholdingLine(models.Model):
    """Withholding Tax Line (Payee Details)"""
    _name = "bir.withholding.line"
    _description = "BIR Withholding Tax Line"

    return_id = fields.Many2one(
        "bir.withholding.return",
        string="WHT Return",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one("res.partner", string="Payee")
    tin = fields.Char(related="partner_id.tin", string="TIN")
    income_type = fields.Selection([
        ("compensation", "Compensation"),
        ("professional_fees", "Professional Fees"),
        ("rental", "Rental"),
        ("interest", "Interest"),
        ("dividends", "Dividends"),
        ("royalties", "Royalties"),
        ("contractor", "Contractor Services"),
        ("other", "Other"),
    ], string="Income Type")
    gross_income = fields.Monetary(string="Gross Income", currency_field="currency_id")
    wht_rate = fields.Float(string="WHT Rate (%)")
    wht_amount = fields.Monetary(string="WHT Amount", currency_field="currency_id")
    move_id = fields.Many2one("account.move", string="Source Invoice")
    payslip_id = fields.Many2one("hr.payslip", string="Source Payslip")
    currency_id = fields.Many2one(
        "res.currency",
        related="return_id.currency_id",
    )


class BirAlphalist(models.Model):
    """Annual Alphalist (Forms 1604-CF, 1604-E)"""
    _name = "bir.alphalist"
    _description = "BIR Annual Alphalist"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Reference", required=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    form_type = fields.Selection([
        ("1604CF", "1604-CF - Compensation"),
        ("1604E", "1604-E - Creditable/Expanded"),
    ], string="Form Type", required=True)
    fiscal_year = fields.Integer(string="Fiscal Year", required=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("generated", "Generated"),
        ("filed", "Filed"),
    ], string="Status", default="draft")
    line_ids = fields.One2many(
        "bir.alphalist.line",
        "alphalist_id",
        string="Payee List",
    )
    total_gross = fields.Monetary(
        string="Total Gross Income",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    total_wht = fields.Monetary(
        string="Total WHT",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    @api.depends("line_ids.gross_income", "line_ids.wht_amount")
    def _compute_totals(self):
        for rec in self:
            rec.total_gross = sum(rec.line_ids.mapped("gross_income"))
            rec.total_wht = sum(rec.line_ids.mapped("wht_amount"))

    def action_generate(self):
        """Generate alphalist from monthly returns"""
        self.ensure_one()
        if self.form_type == "1604CF":
            self._generate_compensation_alphalist()
        else:
            self._generate_expanded_alphalist()
        self.state = "generated"

    def _generate_compensation_alphalist(self):
        """Aggregate all 1601-C returns for the year"""
        domain = [
            ("company_id", "=", self.company_id.id),
            ("form_type", "=", "1601C"),
            ("period_start", ">=", f"{self.fiscal_year}-01-01"),
            ("period_end", "<=", f"{self.fiscal_year}-12-31"),
            ("state", "in", ("filed", "confirmed")),
        ]
        returns = self.env["bir.withholding.return"].search(domain)

        # Aggregate by employee
        employee_data = {}
        for ret in returns:
            for line in ret.line_ids:
                if line.partner_id:
                    key = line.partner_id.id
                    if key not in employee_data:
                        employee_data[key] = {
                            "partner_id": line.partner_id.id,
                            "gross_income": 0,
                            "wht_amount": 0,
                        }
                    employee_data[key]["gross_income"] += line.gross_income
                    employee_data[key]["wht_amount"] += line.wht_amount

        # Create alphalist lines
        lines = [(5, 0, 0)]
        for data in employee_data.values():
            lines.append((0, 0, data))
        self.line_ids = lines

    def _generate_expanded_alphalist(self):
        """Aggregate all 1601-E returns for the year"""
        domain = [
            ("company_id", "=", self.company_id.id),
            ("form_type", "=", "1601E"),
            ("period_start", ">=", f"{self.fiscal_year}-01-01"),
            ("period_end", "<=", f"{self.fiscal_year}-12-31"),
            ("state", "in", ("filed", "confirmed")),
        ]
        returns = self.env["bir.withholding.return"].search(domain)

        # Aggregate by supplier
        supplier_data = {}
        for ret in returns:
            for line in ret.line_ids:
                if line.partner_id:
                    key = line.partner_id.id
                    if key not in supplier_data:
                        supplier_data[key] = {
                            "partner_id": line.partner_id.id,
                            "income_type": line.income_type,
                            "gross_income": 0,
                            "wht_amount": 0,
                        }
                    supplier_data[key]["gross_income"] += line.gross_income
                    supplier_data[key]["wht_amount"] += line.wht_amount

        lines = [(5, 0, 0)]
        for data in supplier_data.values():
            lines.append((0, 0, data))
        self.line_ids = lines


class BirAlphalistLine(models.Model):
    """Alphalist Line (Employee/Supplier Record)"""
    _name = "bir.alphalist.line"
    _description = "BIR Alphalist Line"

    alphalist_id = fields.Many2one(
        "bir.alphalist",
        string="Alphalist",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one("res.partner", string="Payee", required=True)
    tin = fields.Char(related="partner_id.tin", string="TIN")
    income_type = fields.Selection([
        ("compensation", "Compensation"),
        ("professional_fees", "Professional Fees"),
        ("rental", "Rental"),
        ("interest", "Interest"),
        ("dividends", "Dividends"),
        ("other", "Other"),
    ], string="Income Type")
    gross_income = fields.Monetary(string="Total Gross Income", currency_field="currency_id")
    wht_amount = fields.Monetary(string="Total WHT", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        related="alphalist_id.currency_id",
    )
