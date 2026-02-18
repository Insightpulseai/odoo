# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing.

from odoo import models, fields


class HrContract(models.Model):
    """Extend contract with Philippine payroll fields."""

    _inherit = "hr.contract"

    # Compensation Structure
    wage = fields.Monetary(
        string="Monthly Basic Wage",
        help="Basic monthly salary in Philippine Peso",
    )
    wage_type = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("semi_monthly", "Semi-Monthly"),
            ("weekly", "Weekly"),
            ("daily", "Daily"),
        ],
        string="Wage Type",
        default="monthly",
    )

    # Allowances (de minimis benefits - tax exempt)
    rice_subsidy = fields.Monetary(
        string="Rice Subsidy",
        help="Tax-exempt up to PHP 2,000/month",
        default=0.0,
    )
    clothing_allowance = fields.Monetary(
        string="Clothing Allowance",
        help="Tax-exempt up to PHP 6,000/year",
        default=0.0,
    )
    laundry_allowance = fields.Monetary(
        string="Laundry Allowance",
        help="Tax-exempt up to PHP 300/month",
        default=0.0,
    )
    medical_allowance = fields.Monetary(
        string="Medical Allowance",
        help="Tax-exempt up to PHP 10,000/year",
        default=0.0,
    )
    transportation_allowance = fields.Monetary(
        string="Transportation Allowance",
        default=0.0,
    )
    meal_allowance = fields.Monetary(
        string="Meal Allowance",
        default=0.0,
    )

    # Work Schedule
    hours_per_day = fields.Float(
        string="Hours per Day",
        default=8.0,
    )
    working_days_per_month = fields.Float(
        string="Working Days per Month",
        default=22.0,
    )

    # Overtime/Premium Pay Rates
    ot_rate_regular = fields.Float(
        string="OT Rate (Regular)",
        default=1.25,
        help="125% of hourly rate",
    )
    ot_rate_restday = fields.Float(
        string="OT Rate (Rest Day)",
        default=1.30,
        help="130% of daily rate",
    )
    ot_rate_holiday = fields.Float(
        string="OT Rate (Holiday)",
        default=2.00,
        help="200% of daily rate for regular holidays",
    )
    night_diff_rate = fields.Float(
        string="Night Differential Rate",
        default=0.10,
        help="10% additional for 10PM-6AM work",
    )

    # Employment Classification (for statutory compliance)
    employment_type = fields.Selection(
        [
            ("regular", "Regular"),
            ("probationary", "Probationary"),
            ("project", "Project-Based"),
            ("seasonal", "Seasonal"),
            ("fixed_term", "Fixed-Term"),
            ("casual", "Casual"),
        ],
        string="Employment Type",
        default="regular",
    )
    is_minimum_wage = fields.Boolean(
        string="Minimum Wage Earner",
        help="If true, employee is exempt from withholding tax",
    )

    @property
    def daily_rate(self):
        """Compute daily rate from monthly wage."""
        if self.wage and self.working_days_per_month:
            return self.wage / self.working_days_per_month
        return 0.0

    @property
    def hourly_rate(self):
        """Compute hourly rate from daily rate."""
        if self.hours_per_day:
            return self.daily_rate / self.hours_per_day
        return 0.0

    @property
    def total_monthly_compensation(self):
        """Compute total monthly compensation including allowances."""
        return (
            self.wage
            + self.rice_subsidy
            + (self.clothing_allowance / 12)  # Annualized to monthly
            + self.laundry_allowance
            + (self.medical_allowance / 12)  # Annualized to monthly
            + self.transportation_allowance
            + self.meal_allowance
        )
