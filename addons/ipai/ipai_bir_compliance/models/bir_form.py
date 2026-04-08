# -*- coding: utf-8 -*-
from odoo import fields, models


class L10nPhBirForm(models.Model):
    _name = 'l10n.ph.bir.form'
    _description = 'BIR Form'
    _order = 'code'

    code = fields.Char(string='Form Code', required=True, index=True,
                       help='BIR form number (e.g. 0619E, 1601C, 2550Q)')
    name = fields.Char(string='Form Title', required=True)
    tax_domain = fields.Selection([
        ('ewt', 'Expanded Withholding Tax'),
        ('comp', 'Compensation Withholding Tax'),
        ('vat', 'Value Added Tax'),
        ('income', 'Income Tax'),
        ('dst', 'Documentary Stamp Tax'),
        ('percentage', 'Percentage Tax'),
        ('other', 'Other'),
    ], string='Tax Domain', required=True)
    frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('on_transaction', 'Per Transaction'),
    ], string='Filing Frequency', required=True)
    default_channel = fields.Selection([
        ('ebirforms', 'eBIRForms'),
        ('efps', 'eFPS'),
        ('eservices', 'eServices'),
        ('manual', 'Manual'),
    ], string='Default Filing Channel', default='ebirforms')
    has_payment = fields.Boolean(string='Requires Payment', default=True)
    has_attachments = fields.Boolean(string='Has Required Attachments', default=False,
                                     help='Whether alphalists, SAWT/QAP, SLSP etc. are required')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'BIR form code must be unique.'),
    ]
