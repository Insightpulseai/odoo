# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FinancePPMBIRCalendar(models.Model):
    _name = 'finance.ppm.bir.calendar'
    _description = 'BIR Tax Filing Calendar'
    _order = 'filing_deadline asc, form_code asc'

    form_code = fields.Char(
        string='Form Code',
        required=True,
        help='BIR form code (e.g., 1601-C, 2550Q)'
    )
    form_name = fields.Char(
        string='Form Name',
        required=True,
        help='Official BIR form name'
    )
    period = fields.Char(
        string='Period',
        required=True,
        help='Tax period (e.g., 2025-01 for monthly, 2025-Q1 for quarterly)'
    )
    filing_deadline = fields.Date(
        string='Filing Deadline',
        required=True,
        help='Official BIR filing deadline'
    )
    responsible_role = fields.Char(
        string='Responsible Role',
        required=True,
        help='Finance role responsible for filing (e.g., Finance Supervisor)'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of form purpose and coverage'
    )

    _sql_constraints = [
        ('unique_form_period', 'UNIQUE(form_code, period)',
         'BIR form and period combination must be unique!')
    ]

    def name_get(self):
        """Display name: Form Code - Period (Deadline)"""
        result = []
        for record in self:
            name = f"{record.form_code} - {record.period} ({record.filing_deadline})"
            result.append((record.id, name))
        return result
