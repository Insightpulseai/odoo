from odoo import api, fields, models
from odoo.exceptions import UserError


class BirTaxTable(models.Model):
    _name = "ipai.bir.tax.table"
    _description = "BIR Withholding Tax Table"
    _order = "effective_date desc, name"

    name = fields.Char(required=True, help="e.g. Monthly Withholding Tax Table 2023")
    table_type = fields.Selection(
        selection=[
            ("monthly", "Monthly"),
            ("semi_monthly", "Semi-Monthly"),
            ("weekly", "Weekly"),
            ("daily", "Daily"),
        ],
        string="Table Type",
        required=True,
        default="monthly",
    )
    effective_date = fields.Date(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    bracket_ids = fields.One2many(
        "ipai.bir.tax.bracket",
        "table_id",
        string="Tax Brackets",
    )

    def compute_withholding(self, taxable_income):
        """Compute withholding tax for given taxable income using bracket lookup.

        Finds the matching bracket based on the taxable_income falling within
        [range_from, range_to) and applies the formula:
            tax = base_tax + excess_rate * (taxable_income - excess_over)

        Args:
            taxable_income: Monthly (or period-appropriate) taxable compensation.

        Returns:
            float: Computed withholding tax amount (>= 0).

        Raises:
            UserError: If no matching bracket is found.
        """
        self.ensure_one()
        if taxable_income <= 0:
            return 0.0

        brackets = self.bracket_ids.sorted(key=lambda b: b.range_from)
        matched = None
        for bracket in brackets:
            upper = bracket.range_to or float("inf")
            if bracket.range_from <= taxable_income <= upper:
                matched = bracket
                break

        if not matched:
            raise UserError(
                "No matching tax bracket found for taxable income %.2f "
                "in table '%s'." % (taxable_income, self.name)
            )

        excess = max(taxable_income - matched.excess_over, 0.0)
        return matched.base_tax + matched.excess_rate * excess
