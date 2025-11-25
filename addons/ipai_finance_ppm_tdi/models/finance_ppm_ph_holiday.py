# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FinancePPMPHHoliday(models.Model):
    _name = 'finance.ppm.ph.holiday'
    _description = 'Philippine Holiday Calendar'
    _order = 'date asc'

    date = fields.Date(
        string='Holiday Date',
        required=True,
        help='Date of the Philippine holiday'
    )
    name = fields.Char(
        string='Holiday Name',
        required=True,
        help='Official name of the holiday (e.g., New Year\'s Day, Independence Day)'
    )
    holiday_type = fields.Selection([
        ('regular', 'Regular Holiday'),
        ('special', 'Special Non-Working Day'),
        ('local', 'Local Holiday')
    ], string='Holiday Type', required=True, help='Classification of holiday under Philippine law')

    is_nationwide = fields.Boolean(
        string='Nationwide',
        default=True,
        help='True if holiday applies nationwide, False if local/regional'
    )
    description = fields.Text(
        string='Description',
        help='Additional information about the holiday'
    )

    _sql_constraints = [
        ('unique_date_name', 'UNIQUE(date, name)',
         'Holiday date and name combination must be unique!')
    ]

    @api.model
    def is_business_day(self, check_date):
        """Check if a given date is a business day (not a holiday or weekend)"""
        # Check if weekend (Saturday=5, Sunday=6 in Python weekday())
        if check_date.weekday() >= 5:
            return False

        # Check if holiday
        holiday = self.search([('date', '=', check_date)], limit=1)
        if holiday:
            return False

        return True

    @api.model
    def get_next_business_day(self, start_date, days_forward=1):
        """Get the next business day N days forward from start_date"""
        from datetime import timedelta
        current_date = start_date
        business_days_counted = 0

        while business_days_counted < days_forward:
            current_date += timedelta(days=1)
            if self.is_business_day(current_date):
                business_days_counted += 1

        return current_date

    def name_get(self):
        """Display name: Holiday Name (Date)"""
        result = []
        for record in self:
            name = f"{record.name} ({record.date})"
            result.append((record.id, name))
        return result
