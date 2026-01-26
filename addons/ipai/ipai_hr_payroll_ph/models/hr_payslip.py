# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing.

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import logging

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    """Philippine Payslip with statutory deductions and BIR compliance."""

    _name = "hr.payslip"
    _description = "Employee Payslip"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, employee_id"

    name = fields.Char(
        string="Payslip Name",
        compute="_compute_name",
        store=True,
        readonly=False,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        tracking=True,
    )
    contract_id = fields.Many2one(
        "hr.contract",
        string="Contract",
        compute="_compute_contract",
        store=True,
    )
    date_from = fields.Date(
        string="Period Start",
        required=True,
        default=lambda self: date.today().replace(day=1),
    )
    date_to = fields.Date(
        string="Period End",
        required=True,
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
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("verify", "Waiting Verification"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    # Earnings
    basic_salary = fields.Monetary(
        string="Basic Salary",
        compute="_compute_earnings",
        store=True,
    )
    overtime_pay = fields.Monetary(string="Overtime Pay", default=0.0)
    holiday_pay = fields.Monetary(string="Holiday Pay", default=0.0)
    night_differential = fields.Monetary(string="Night Differential", default=0.0)
    allowances = fields.Monetary(string="Allowances", default=0.0)
    bonus = fields.Monetary(string="Bonus/13th Month", default=0.0)
    other_earnings = fields.Monetary(string="Other Earnings", default=0.0)

    gross_wage = fields.Monetary(
        string="Gross Wage",
        compute="_compute_gross_wage",
        store=True,
    )

    # SSS Contributions (2025 rates)
    sss_ee = fields.Monetary(
        string="SSS (Employee)",
        compute="_compute_ph_contributions",
        store=True,
        help="Employee share: 5% of Monthly Salary Credit (max PHP 35,000 MSC)",
    )
    sss_er = fields.Monetary(
        string="SSS (Employer)",
        compute="_compute_ph_contributions",
        store=True,
        help="Employer share: 10% of Monthly Salary Credit",
    )
    sss_ec = fields.Monetary(
        string="SSS EC",
        compute="_compute_ph_contributions",
        store=True,
        help="Employees' Compensation (included in ER share)",
    )

    # PhilHealth Contributions (2025 rates)
    philhealth_ee = fields.Monetary(
        string="PhilHealth (Employee)",
        compute="_compute_ph_contributions",
        store=True,
        help="Employee share: 2.5% (max base PHP 100,000)",
    )
    philhealth_er = fields.Monetary(
        string="PhilHealth (Employer)",
        compute="_compute_ph_contributions",
        store=True,
        help="Employer share: 2.5%",
    )

    # Pag-IBIG Contributions (2025 rates)
    pagibig_ee = fields.Monetary(
        string="Pag-IBIG (Employee)",
        compute="_compute_ph_contributions",
        store=True,
        help="Employee share: 2% (max base PHP 5,000 for standard)",
    )
    pagibig_er = fields.Monetary(
        string="Pag-IBIG (Employer)",
        compute="_compute_ph_contributions",
        store=True,
        help="Employer share: 2%",
    )

    # BIR Withholding Tax
    taxable_income = fields.Monetary(
        string="Taxable Income",
        compute="_compute_bir_tax",
        store=True,
        help="Gross wage minus mandatory contributions",
    )
    withholding_tax = fields.Monetary(
        string="Withholding Tax",
        compute="_compute_bir_tax",
        store=True,
        help="BIR TRAIN Law withholding tax",
    )

    # Other Deductions
    sss_loan = fields.Monetary(string="SSS Loan", default=0.0)
    pagibig_loan = fields.Monetary(string="Pag-IBIG Loan", default=0.0)
    company_loan = fields.Monetary(string="Company Loan", default=0.0)
    other_deductions = fields.Monetary(string="Other Deductions", default=0.0)

    # Totals
    total_deductions = fields.Monetary(
        string="Total Deductions",
        compute="_compute_totals",
        store=True,
    )
    net_wage = fields.Monetary(
        string="Net Wage",
        compute="_compute_totals",
        store=True,
    )
    total_employer_cost = fields.Monetary(
        string="Employer Cost",
        compute="_compute_totals",
        store=True,
        help="Gross wage + employer contributions",
    )

    # BIR Integration
    bir_return_id = fields.Many2one(
        "bir.withholding.return",
        string="BIR 1601-C Return",
        readonly=True,
    )

    @api.depends("employee_id", "date_from")
    def _compute_name(self):
        for slip in self:
            if slip.employee_id and slip.date_from:
                period = slip.date_from.strftime("%B %Y")
                slip.name = f"{slip.employee_id.name} - {period}"
            else:
                slip.name = "New Payslip"

    @api.depends("employee_id", "date_from")
    def _compute_contract(self):
        for slip in self:
            if slip.employee_id:
                contract = self.env["hr.contract"].search(
                    [
                        ("employee_id", "=", slip.employee_id.id),
                        ("state", "=", "open"),
                        ("date_start", "<=", slip.date_from),
                        "|",
                        ("date_end", ">=", slip.date_from),
                        ("date_end", "=", False),
                    ],
                    limit=1,
                )
                slip.contract_id = contract
            else:
                slip.contract_id = False

    @api.depends("contract_id")
    def _compute_earnings(self):
        for slip in self:
            if slip.contract_id:
                slip.basic_salary = slip.contract_id.wage
            else:
                slip.basic_salary = 0.0

    @api.depends(
        "basic_salary",
        "overtime_pay",
        "holiday_pay",
        "night_differential",
        "allowances",
        "bonus",
        "other_earnings",
    )
    def _compute_gross_wage(self):
        for slip in self:
            slip.gross_wage = (
                slip.basic_salary
                + slip.overtime_pay
                + slip.holiday_pay
                + slip.night_differential
                + slip.allowances
                + slip.bonus
                + slip.other_earnings
            )

    @api.depends("gross_wage", "employee_id")
    def _compute_ph_contributions(self):
        """Compute SSS, PhilHealth, Pag-IBIG based on 2025 tables."""
        for slip in self:
            gross = Decimal(str(slip.gross_wage or 0))

            # ===== SSS 2025 =====
            # Total: 15% (5% EE + 10% ER)
            # MSC range: PHP 4,000 - 35,000
            sss_msc_min = Decimal("4000")
            sss_msc_max = Decimal("35000")
            sss_base = min(max(gross, sss_msc_min), sss_msc_max)

            slip.sss_ee = float(
                (sss_base * Decimal("0.05")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
            slip.sss_er = float(
                (sss_base * Decimal("0.10")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
            slip.sss_ec = float(
                (sss_base * Decimal("0.01")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )  # EC included in ER

            # ===== PhilHealth 2025 =====
            # Total: 5% (2.5% EE + 2.5% ER)
            # Base range: PHP 10,000 - 100,000
            ph_base_min = Decimal("10000")
            ph_base_max = Decimal("100000")
            ph_base = min(max(gross, ph_base_min), ph_base_max)

            slip.philhealth_ee = float(
                (ph_base * Decimal("0.025")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
            slip.philhealth_er = float(
                (ph_base * Decimal("0.025")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )

            # ===== Pag-IBIG 2025 =====
            # Total: 4% (2% EE + 2% ER)
            # Standard: max base PHP 5,000
            pagibig_base_max = Decimal("5000")
            pagibig_base = min(gross, pagibig_base_max)

            slip.pagibig_ee = float(
                (pagibig_base * Decimal("0.02")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
            slip.pagibig_er = float(
                (pagibig_base * Decimal("0.02")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )

    @api.depends("gross_wage", "sss_ee", "philhealth_ee", "pagibig_ee", "employee_id")
    def _compute_bir_tax(self):
        """Compute BIR withholding tax using TRAIN Law tables (2025)."""
        for slip in self:
            gross = Decimal(str(slip.gross_wage or 0))
            sss = Decimal(str(slip.sss_ee or 0))
            ph = Decimal(str(slip.philhealth_ee or 0))
            pi = Decimal(str(slip.pagibig_ee or 0))

            # Taxable income = gross - mandatory contributions
            taxable = gross - sss - ph - pi
            slip.taxable_income = float(taxable)

            # BIR TRAIN Law Monthly Tax Table (2018-2022 extended)
            # Bracket: (min, max, base_tax, rate_over_min)
            tax_table = [
                (Decimal("0"), Decimal("20833"), Decimal("0"), Decimal("0")),
                (
                    Decimal("20833"),
                    Decimal("33333"),
                    Decimal("0"),
                    Decimal("0.15"),
                ),
                (
                    Decimal("33333"),
                    Decimal("66667"),
                    Decimal("1875"),
                    Decimal("0.20"),
                ),
                (
                    Decimal("66667"),
                    Decimal("166667"),
                    Decimal("8541.80"),
                    Decimal("0.25"),
                ),
                (
                    Decimal("166667"),
                    Decimal("666667"),
                    Decimal("33541.80"),
                    Decimal("0.30"),
                ),
                (
                    Decimal("666667"),
                    Decimal("999999999"),
                    Decimal("183541.80"),
                    Decimal("0.35"),
                ),
            ]

            tax = Decimal("0")
            for bracket_min, bracket_max, base_tax, rate in tax_table:
                if bracket_min < taxable <= bracket_max:
                    tax = base_tax + ((taxable - bracket_min) * rate)
                    break
                elif taxable > bracket_max:
                    continue

            slip.withholding_tax = float(
                tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            )

    @api.depends(
        "sss_ee",
        "philhealth_ee",
        "pagibig_ee",
        "withholding_tax",
        "sss_loan",
        "pagibig_loan",
        "company_loan",
        "other_deductions",
        "gross_wage",
        "sss_er",
        "philhealth_er",
        "pagibig_er",
    )
    def _compute_totals(self):
        for slip in self:
            slip.total_deductions = (
                slip.sss_ee
                + slip.philhealth_ee
                + slip.pagibig_ee
                + slip.withholding_tax
                + slip.sss_loan
                + slip.pagibig_loan
                + slip.company_loan
                + slip.other_deductions
            )
            slip.net_wage = slip.gross_wage - slip.total_deductions
            slip.total_employer_cost = (
                slip.gross_wage + slip.sss_er + slip.philhealth_er + slip.pagibig_er
            )

    def action_verify(self):
        """Submit for verification."""
        self.write({"state": "verify"})

    def action_done(self):
        """Confirm payslip."""
        for slip in self:
            if slip.state != "verify":
                raise UserError("Payslip must be verified before confirmation.")
        self.write({"state": "done"})

    def action_draft(self):
        """Reset to draft."""
        self.write({"state": "draft"})

    def action_cancel(self):
        """Cancel payslip."""
        self.write({"state": "cancel"})

    def action_compute_sheet(self):
        """Recompute all payslip values."""
        for slip in self:
            slip._compute_earnings()
            slip._compute_gross_wage()
            slip._compute_ph_contributions()
            slip._compute_bir_tax()
            slip._compute_totals()
        return True
