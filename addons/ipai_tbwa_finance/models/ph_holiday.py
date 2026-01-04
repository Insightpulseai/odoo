from datetime import date, timedelta

from odoo import api, fields, models


class PhHoliday(models.Model):
    """Philippine Holiday Calendar - Shared across all finance tasks"""

    _name = "ph.holiday"
    _description = "Philippine Holiday"
    _order = "date"

    name = fields.Char(string="Holiday Name", required=True)
    date = fields.Date(string="Date", required=True, index=True)
    holiday_type = fields.Selection(
        [
            ("regular", "Regular Holiday"),
            ("special", "Special Non-Working Day"),
            ("special_working", "Special Working Day"),
        ],
        string="Type",
        required=True,
        default="regular",
    )
    year = fields.Integer(
        string="Year",
        compute="_compute_year",
        store=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    _sql_constraints = [
        (
            "date_unique",
            "unique(date, company_id)",
            "Holiday date must be unique per company",
        ),
    ]

    @api.depends("date")
    def _compute_year(self):
        for rec in self:
            rec.year = rec.date.year if rec.date else False

    @api.model
    def is_holiday(self, check_date, company_id=None):
        """Check if a date is a holiday"""
        domain = [("date", "=", check_date)]
        if company_id:
            domain.append(("company_id", "in", [company_id, False]))
        return bool(self.search_count(domain))

    @api.model
    def is_workday(self, check_date, company_id=None):
        """Check if a date is a workday (not weekend, not holiday)"""
        if check_date.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
        return not self.is_holiday(check_date, company_id)

    @api.model
    def get_workday_offset(self, base_date, offset_days, company_id=None):
        """
        Calculate workday offset from base_date.
        Positive offset = future workdays
        Negative offset = past workdays
        """
        current = base_date
        days_counted = 0
        direction = 1 if offset_days >= 0 else -1
        target = abs(offset_days)

        while days_counted < target:
            current += timedelta(days=direction)
            if self.is_workday(current, company_id):
                days_counted += 1

        return current

    @api.model
    def get_last_workday_of_month(self, year, month, company_id=None):
        """Get last working day of a given month"""
        # Start from last day of month
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        last_day = next_month - timedelta(days=1)

        # Walk back until we find a workday
        while not self.is_workday(last_day, company_id):
            last_day -= timedelta(days=1)

        return last_day

    @api.model
    def count_workdays_between(self, start_date, end_date, company_id=None):
        """Count workdays between two dates (inclusive)"""
        count = 0
        current = start_date
        while current <= end_date:
            if self.is_workday(current, company_id):
                count += 1
            current += timedelta(days=1)
        return count
