# -*- coding: utf-8 -*-
from odoo import fields, models


class L10nPhBirServiceEndpoint(models.Model):
    _name = 'l10n.ph.bir.service.endpoint'
    _description = 'BIR Service Endpoint'
    _order = 'code'

    code = fields.Char(string='Code', required=True, index=True)
    name = fields.Char(string='Service Name', required=True)
    service_type = fields.Selection([
        ('filing', 'Filing'),
        ('payment', 'Payment'),
        ('registration', 'Registration'),
        ('reference', 'Reference'),
    ], string='Service Type', required=True)
    official_url = fields.Char(string='Official URL')
    supports_filing = fields.Boolean(string='Supports Filing')
    supports_payment = fields.Boolean(string='Supports Payment')
    supports_reference = fields.Boolean(string='Supports Reference/Download')
    current_version = fields.Char(string='Current Version',
                                   help='For eBIRForms: offline package version')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Service endpoint code must be unique.'),
    ]
