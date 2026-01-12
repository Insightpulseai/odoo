# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class IpaiTenant(models.Model):
    _name = 'ipai.tenant'
    _description = 'Platform Tenant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, code'

    # Basic Info
    name = fields.Char(
        string='Tenant Name',
        required=True,
        tracking=True,
        help='Display name for the tenant (e.g., "TBWA Philippines")'
    )
    code = fields.Char(
        string='Tenant Code',
        required=True,
        size=16,
        tracking=True,
        help='Unique identifier for tenant (e.g., "tbwa", lowercase alphanumeric)'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order in lists'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True
    )

    # Technical Configuration
    db_name = fields.Char(
        string='Odoo Database',
        required=True,
        help='Odoo database name for this tenant (e.g., "odoo_tbwa")'
    )
    supabase_schema = fields.Char(
        string='Supabase Schema',
        required=True,
        help='PostgreSQL schema in Supabase (e.g., "tbwa", "scout")'
    )
    primary_domain = fields.Char(
        string='Primary Domain',
        help='Primary domain for tenant access (e.g., "tbwa.erp.insightpulseai.net")'
    )

    # Superset Integration
    superset_workspace = fields.Char(
        string='Superset Workspace',
        help='Superset workspace/folder for tenant dashboards'
    )
    superset_base_url = fields.Char(
        string='Superset Base URL',
        default='https://superset.insightpulseai.net',
        help='Base URL for Superset instance'
    )

    # Business Info
    company_name = fields.Char(
        string='Legal Company Name',
        tracking=True
    )
    industry = fields.Selection(
        [
            ('advertising', 'Advertising & Marketing'),
            ('retail', 'Retail'),
            ('finance', 'Financial Services'),
            ('manufacturing', 'Manufacturing'),
            ('services', 'Professional Services'),
            ('other', 'Other'),
        ],
        string='Industry',
        default='advertising'
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        default=lambda self: self.env.ref('base.ph').id
    )

    # Contact Info
    admin_email = fields.Char(
        string='Admin Email',
        tracking=True
    )
    admin_phone = fields.Char(
        string='Admin Phone'
    )

    # Metadata
    onboarded_date = fields.Date(
        string='Onboarding Date',
        default=fields.Date.context_today,
        tracking=True
    )
    notes = fields.Text(
        string='Internal Notes'
    )

    # Constraints
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Tenant code must be unique!'),
        ('db_name_unique', 'UNIQUE(db_name)', 'Database name must be unique!'),
    ]

    @api.constrains('code')
    def _check_code_format(self):
        """Validate tenant code format (lowercase alphanumeric + underscore)"""
        for record in self:
            if record.code and not re.match(r'^[a-z0-9_]+$', record.code):
                raise ValidationError(_(
                    'Tenant code must contain only lowercase letters, numbers, and underscores.'
                ))

    @api.constrains('supabase_schema')
    def _check_schema_format(self):
        """Validate Supabase schema format"""
        for record in self:
            if record.supabase_schema and not re.match(r'^[a-z_][a-z0-9_]*$', record.supabase_schema):
                raise ValidationError(_(
                    'Supabase schema must be a valid PostgreSQL schema name '
                    '(start with letter/underscore, contain only lowercase letters, numbers, underscores).'
                ))

    def name_get(self):
        """Display tenant as 'Code - Name'"""
        result = []
        for record in self:
            name = f'[{record.code}] {record.name}'
            result.append((record.id, name))
        return result

    def action_provision_supabase_schema(self):
        """Action to provision Supabase schema for tenant"""
        self.ensure_one()
        # This would trigger external script/API to create schema
        # Implementation depends on your Supabase CLI setup
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Schema Provisioning'),
                'message': _('Supabase schema provisioning for %s initiated.') % self.code,
                'type': 'info',
                'sticky': False,
            }
        }

    def action_open_superset_workspace(self):
        """Open Superset workspace for tenant"""
        self.ensure_one()
        if not self.superset_base_url:
            raise ValidationError(_('Superset base URL not configured for this tenant.'))

        url = f'{self.superset_base_url}/superset/dashboard/'
        if self.superset_workspace:
            url += f'?workspace={self.superset_workspace}'

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
