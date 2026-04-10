# -*- coding: utf-8 -*-
from odoo import fields, models


class HrExpensePolicyViolation(models.Model):
    """Policy violation tracking for expense reports."""

    _name = 'hr.expense.policy.violation'
    _description = 'Cash Advance Policy Violation'
    _order = 'create_date desc'

    liquidation_id = fields.Many2one(
        'hr.expense.liquidation', string='Cash Advance',
        required=True, ondelete='cascade', index=True,
    )
    rule_code = fields.Char(
        string='Rule Code', required=True,
        help='MAX_AMOUNT, RECEIPT_REQUIRED, CATEGORY_LIMIT, OVERDUE_CHECK',
    )
    severity = fields.Selection([
        ('warning', 'Warning'),
        ('block', 'Blocking'),
    ], string='Severity', required=True)
    description = fields.Text(string='Description')
    resolved = fields.Boolean(string='Resolved', default=False)
    resolved_by = fields.Many2one('res.users', string='Resolved By')
    resolved_date = fields.Datetime(string='Resolved Date')
