# -*- coding: utf-8 -*-
from odoo import fields, models


class HrExpensePolicyRule(models.Model):
    _name = 'hr.expense.policy.rule'
    _description = 'Expense Policy Rule'
    _order = 'sequence, id'

    name = fields.Char(string='Rule Name', required=True)
    rule_code = fields.Char(
        string='Rule Code', required=True, index=True,
        help='Unique code: MAX_AMOUNT, RECEIPT_REQUIRED, CATEGORY_LIMIT, OVERDUE_CHECK',
    )
    rule_type = fields.Selection([
        ('amount_limit', 'Amount Limit'),
        ('receipt_required', 'Receipt Required'),
        ('category_limit', 'Category Limit'),
        ('overdue_check', 'Overdue Check'),
    ], string='Rule Type', required=True)
    threshold_amount = fields.Float(string='Threshold Amount')
    max_days = fields.Integer(string='Max Days', help='For overdue checks')
    severity = fields.Selection([
        ('warning', 'Warning'),
        ('block', 'Blocking'),
    ], string='Severity', required=True, default='warning')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
    )
