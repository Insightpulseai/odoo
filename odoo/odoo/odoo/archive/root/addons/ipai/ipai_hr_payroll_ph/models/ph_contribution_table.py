# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing.

from odoo import models, fields, api
from decimal import Decimal, ROUND_HALF_UP


class SSSContributionTable(models.Model):
    """SSS Contribution Table based on Monthly Salary Credit (MSC)."""

    _name = "ph.sss.contribution.table"
    _description = "SSS Contribution Table"
    _order = "msc_min"

    name = fields.Char(compute="_compute_name", store=True)
    year = fields.Integer(default=2025, required=True)
    active = fields.Boolean(default=True)

    # Salary Credit Range
    msc_min = fields.Float(string="MSC From", required=True)
    msc_max = fields.Float(string="MSC To", required=True)
    msc = fields.Float(string="Monthly Salary Credit", required=True)

    # Contribution Rates (2025)
    ee_rate = fields.Float(string="EE Rate", default=0.05)  # 5%
    er_rate = fields.Float(string="ER Rate", default=0.10)  # 10%
    total_rate = fields.Float(string="Total Rate", default=0.15)  # 15%

    # Fixed Amounts
    ee_contribution = fields.Float(string="EE Contribution", compute="_compute_contributions", store=True)
    er_contribution = fields.Float(string="ER Contribution", compute="_compute_contributions", store=True)
    ec_contribution = fields.Float(string="EC Contribution", default=0.0)
    total_contribution = fields.Float(string="Total Contribution", compute="_compute_contributions", store=True)

    @api.depends("msc_min", "msc_max")
    def _compute_name(self):
        for rec in self:
            rec.name = f"SSS {rec.year}: PHP {rec.msc_min:,.0f} - {rec.msc_max:,.0f}"

    @api.depends("msc", "ee_rate", "er_rate")
    def _compute_contributions(self):
        for rec in self:
            rec.ee_contribution = rec.msc * rec.ee_rate
            rec.er_contribution = rec.msc * rec.er_rate
            rec.total_contribution = rec.ee_contribution + rec.er_contribution

    @api.model
    def get_contribution(self, gross_wage, year=2025):
        """Get SSS contributions for a given gross wage."""
        table = self.search([
            ("year", "=", year),
            ("msc_min", "<=", gross_wage),
            ("msc_max", ">=", gross_wage),
            ("active", "=", True),
        ], limit=1)

        if table:
            return {
                "ee": table.ee_contribution,
                "er": table.er_contribution,
                "ec": table.ec_contribution,
                "total": table.total_contribution,
            }

        # Fallback: compute directly for max bracket
        msc = min(max(gross_wage, 4000), 35000)
        return {
            "ee": msc * 0.05,
            "er": msc * 0.10,
            "ec": 0,
            "total": msc * 0.15,
        }


class PhilHealthTable(models.Model):
    """PhilHealth Premium Rate Table."""

    _name = "ph.philhealth.table"
    _description = "PhilHealth Premium Table"

    name = fields.Char(default="PhilHealth 2025")
    year = fields.Integer(default=2025, required=True)
    active = fields.Boolean(default=True)

    # Rate Configuration
    premium_rate = fields.Float(string="Premium Rate", default=0.05)  # 5% total
    ee_share = fields.Float(string="EE Share", default=0.50)  # 50% of premium
    er_share = fields.Float(string="ER Share", default=0.50)  # 50% of premium

    # Income Floor/Ceiling
    income_floor = fields.Float(string="Income Floor", default=10000)
    income_ceiling = fields.Float(string="Income Ceiling", default=100000)

    @api.model
    def get_contribution(self, gross_wage, year=2025):
        """Get PhilHealth contributions for a given gross wage."""
        table = self.search([("year", "=", year), ("active", "=", True)], limit=1)

        if table:
            base = min(max(gross_wage, table.income_floor), table.income_ceiling)
            premium = base * table.premium_rate
            return {
                "ee": premium * table.ee_share,
                "er": premium * table.er_share,
                "total": premium,
            }

        # Fallback: 2025 defaults
        base = min(max(gross_wage, 10000), 100000)
        premium = base * 0.05
        return {
            "ee": premium * 0.50,
            "er": premium * 0.50,
            "total": premium,
        }


class PagIBIGTable(models.Model):
    """Pag-IBIG Contribution Table."""

    _name = "ph.pagibig.table"
    _description = "Pag-IBIG Contribution Table"

    name = fields.Char(default="Pag-IBIG 2025")
    year = fields.Integer(default=2025, required=True)
    active = fields.Boolean(default=True)

    # Rate Configuration
    contribution_type = fields.Selection([
        ("regular", "Regular (2%)"),
        ("modified_1", "Modified Pag-IBIG 1"),
        ("modified_2", "Modified Pag-IBIG 2"),
    ], default="regular")

    ee_rate = fields.Float(string="EE Rate", default=0.02)  # 2%
    er_rate = fields.Float(string="ER Rate", default=0.02)  # 2%

    # Income ceiling for regular contribution
    income_ceiling = fields.Float(string="Income Ceiling", default=5000)

    @api.model
    def get_contribution(self, gross_wage, contribution_type="regular", year=2025):
        """Get Pag-IBIG contributions for a given gross wage."""
        table = self.search([
            ("year", "=", year),
            ("contribution_type", "=", contribution_type),
            ("active", "=", True),
        ], limit=1)

        if table:
            base = min(gross_wage, table.income_ceiling)
            return {
                "ee": base * table.ee_rate,
                "er": base * table.er_rate,
                "total": base * (table.ee_rate + table.er_rate),
            }

        # Fallback: regular 2% each, max 5000 base
        base = min(gross_wage, 5000)
        return {
            "ee": base * 0.02,
            "er": base * 0.02,
            "total": base * 0.04,
        }


class BIRTaxTable(models.Model):
    """BIR Withholding Tax Table (TRAIN Law)."""

    _name = "ph.bir.tax.table"
    _description = "BIR Withholding Tax Table"
    _order = "bracket_min"

    name = fields.Char(compute="_compute_name", store=True)
    year = fields.Integer(default=2025, required=True)
    period = fields.Selection([
        ("annual", "Annual"),
        ("monthly", "Monthly"),
        ("semi_monthly", "Semi-Monthly"),
        ("weekly", "Weekly"),
        ("daily", "Daily"),
    ], default="monthly", required=True)
    active = fields.Boolean(default=True)

    # Bracket Range
    bracket_min = fields.Float(string="Over", required=True)
    bracket_max = fields.Float(string="But Not Over", required=True)

    # Tax Computation
    base_tax = fields.Float(string="Base Tax", default=0.0)
    tax_rate = fields.Float(string="Tax Rate (%)", default=0.0)

    @api.depends("bracket_min", "bracket_max", "period")
    def _compute_name(self):
        for rec in self:
            rec.name = f"BIR {rec.year} ({rec.period}): PHP {rec.bracket_min:,.0f} - {rec.bracket_max:,.0f}"

    @api.model
    def compute_tax(self, taxable_income, period="monthly", year=2025):
        """Compute withholding tax for given taxable income."""
        table = self.search([
            ("year", "=", year),
            ("period", "=", period),
            ("bracket_min", "<", taxable_income),
            ("bracket_max", ">=", taxable_income),
            ("active", "=", True),
        ], limit=1)

        if table:
            excess = taxable_income - table.bracket_min
            tax = table.base_tax + (excess * table.tax_rate / 100)
            return round(tax, 2)

        # Fallback: TRAIN Law monthly table
        if taxable_income <= 20833:
            return 0.0
        elif taxable_income <= 33333:
            return (taxable_income - 20833) * 0.15
        elif taxable_income <= 66667:
            return 1875 + (taxable_income - 33333) * 0.20
        elif taxable_income <= 166667:
            return 8541.80 + (taxable_income - 66667) * 0.25
        elif taxable_income <= 666667:
            return 33541.80 + (taxable_income - 166667) * 0.30
        else:
            return 183541.80 + (taxable_income - 666667) * 0.35
