# -*- coding: utf-8 -*-
import json
from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class L10nPhBirDeadlineRule(models.Model):
    _name = 'l10n.ph.bir.deadline.rule'
    _description = 'BIR Deadline Rule'
    _order = 'form_id, rule_code'

    form_id = fields.Many2one('l10n.ph.bir.form', string='BIR Form',
                               required=True, ondelete='cascade')
    rule_code = fields.Char(string='Rule Code', required=True, index=True,
                            help='Machine-readable deadline rule identifier')
    rule_kind = fields.Selection([
        ('relative_monthly', 'Relative Monthly (Nth day of next month)'),
        ('relative_quarterly', 'Relative Quarterly (Nth day after quarter end)'),
        ('fixed_quarterly', 'Fixed Quarterly (specific month/day per quarter)'),
        ('fixed_annual', 'Fixed Annual (specific month/day)'),
    ], string='Rule Kind', required=True)
    month_offset = fields.Integer(string='Month Offset', default=1,
                                   help='Months after period end (e.g. 1 = next month)')
    day_of_month = fields.Integer(string='Day of Month',
                                   help='Due day within the target month (e.g. 10, 25, 31)')
    quarter_position = fields.Integer(string='Quarter Position',
                                      help='Which quarter month (1, 2, or 3)')
    fixed_month = fields.Integer(string='Fixed Month',
                                  help='For annual rules: month number (1-12)')
    fixed_day = fields.Integer(string='Fixed Day',
                                help='For annual rules: day of month')
    special_case_json = fields.Text(string='Special Cases (JSON)',
                                     help='JSON dict for exceptions, e.g. December to Jan 25 for 1601C')
    deadline_source = fields.Selection([
        ('form_instruction', 'BIR Form Instruction'),
        ('interactive_tax_calendar', 'BIR Interactive Tax Calendar'),
        ('revenue_issuance_override', 'Revenue Issuance Override'),
    ], string='Deadline Source', default='form_instruction', required=True)
    is_efps_variant = fields.Boolean(string='eFPS Variant',
                                      help='eFPS filers may have different deadlines per issuance')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('rule_code_uniq', 'unique(rule_code)', 'Deadline rule code must be unique.'),
    ]

    def compute_due_date(self, period_start, period_end):
        """Compute the due date for a given period based on this rule.

        Args:
            period_start: date - start of the filing period
            period_end: date - end of the filing period

        Returns:
            date - the computed due date
        """
        self.ensure_one()

        # Check special cases first
        special = {}
        if self.special_case_json:
            try:
                special = json.loads(self.special_case_json)
            except (json.JSONDecodeError, TypeError):
                special = {}

        # Check if period_end month has a special case
        month_key = str(period_end.month)
        if month_key in special:
            sc = special[month_key]
            return date(
                period_end.year + (1 if sc.get('next_year') else 0),
                sc['month'],
                sc['day'],
            )

        if self.rule_kind == 'relative_monthly':
            # Nth day of the month after period_end + month_offset
            target_month = period_end.month + self.month_offset
            target_year = period_end.year
            while target_month > 12:
                target_month -= 12
                target_year += 1
            day = min(self.day_of_month, self._last_day_of_month(target_year, target_month))
            return date(target_year, target_month, day)

        elif self.rule_kind == 'relative_quarterly':
            # Nth day of the month following quarter end
            target_month = period_end.month + self.month_offset
            target_year = period_end.year
            while target_month > 12:
                target_month -= 12
                target_year += 1
            day = min(self.day_of_month or 31, self._last_day_of_month(target_year, target_month))
            return date(target_year, target_month, day)

        elif self.rule_kind == 'fixed_quarterly':
            # Fixed dates per quarter (e.g. Apr 15, Aug 15, Nov 15 for 1701Q)
            # special_case_json maps quarter number to {month, day}
            quarter = (period_end.month - 1) // 3 + 1
            quarter_key = str(quarter)
            if quarter_key in special:
                sc = special[quarter_key]
                return date(period_end.year, sc['month'], sc['day'])
            if self.fixed_month and self.fixed_day:
                return date(period_end.year, self.fixed_month, self.fixed_day)
            raise UserError(_('Fixed quarterly rule %s missing quarter mapping.') % self.rule_code)

        elif self.rule_kind == 'fixed_annual':
            # Fixed date each year (e.g. Apr 15 for 1701)
            target_year = period_end.year + 1  # typically filed for prior year
            return date(target_year, self.fixed_month, self.fixed_day)

        raise UserError(_('Unknown rule kind: %s') % self.rule_kind)

    @staticmethod
    def _last_day_of_month(year, month):
        """Return the last day of the given month."""
        if month == 12:
            return 31
        next_month = date(year, month + 1, 1)
        return (next_month - timedelta(days=1)).day
