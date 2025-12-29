# -*- coding: utf-8 -*-
"""
Superset Dataset Model

Manages datasets (tables/views) exposed to Apache Superset.
Handles SQL view generation, metadata sync, and RLS configuration.
"""
import json
import logging
import re

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import sql

_logger = logging.getLogger(__name__)


class SupersetDataset(models.Model):
    _name = 'superset.dataset'
    _description = 'Superset Dataset'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(
        string='Dataset Name',
        required=True,
        tracking=True,
    )
    technical_name = fields.Char(
        string='Technical Name',
        required=True,
        help='Name used in SQL view (snake_case, no spaces)',
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    
    # Connection
    connection_id = fields.Many2one(
        'superset.connection',
        string='Superset Connection',
        required=True,
        ondelete='cascade',
    )
    
    # Superset IDs
    superset_dataset_id = fields.Integer(
        string='Superset Dataset ID',
        readonly=True,
        help='ID of dataset in Superset',
    )
    
    # Source Configuration
    source_type = fields.Selection([
        ('model', 'Odoo Model'),
        ('sql', 'Custom SQL'),
        ('view', 'SQL View'),
    ], string='Source Type', default='model', required=True)
    
    # For model-based datasets
    model_id = fields.Many2one(
        'ir.model',
        string='Odoo Model',
        domain=[('transient', '=', False)],
    )
    model_name = fields.Char(
        string='Model Name',
        related='model_id.model',
        store=True,
    )
    
    # Field Selection
    field_ids = fields.Many2many(
        'ir.model.fields',
        string='Included Fields',
        domain="[('model_id', '=', model_id), ('ttype', 'not in', ['one2many', 'binary'])]",
    )
    include_all_fields = fields.Boolean(
        string='Include All Fields',
        default=False,
        help='Include all scalar fields from the model',
    )
    
    # For SQL-based datasets
    custom_sql = fields.Text(
        string='Custom SQL',
        help='Custom SQL query for the dataset',
    )
    
    # SQL View Management
    view_name = fields.Char(
        string='SQL View Name',
        compute='_compute_view_name',
        store=True,
    )
    view_sql = fields.Text(
        string='Generated SQL',
        readonly=True,
    )
    view_created = fields.Boolean(
        string='View Created',
        readonly=True,
    )
    
    # Multi-tenant / RLS
    enable_rls = fields.Boolean(
        string='Enable Row-Level Security',
        default=True,
        help='Filter data by company_id for multi-tenant access',
    )
    rls_filter_column = fields.Char(
        string='RLS Filter Column',
        default='company_id',
        help='Column to use for row-level security filtering',
    )
    
    # Categorization
    category = fields.Selection([
        ('sales', 'Sales & CRM'),
        ('finance', 'Finance & Accounting'),
        ('inventory', 'Inventory & Warehouse'),
        ('hr', 'Human Resources'),
        ('project', 'Project Management'),
        ('custom', 'Custom'),
    ], string='Category', default='custom')
    
    # Metadata
    description = fields.Text(string='Description')
    column_count = fields.Integer(
        string='Columns',
        compute='_compute_column_count',
    )
    last_sync = fields.Datetime(string='Last Sync', readonly=True)
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error'),
    ], string='Sync Status', default='pending', readonly=True)
    sync_error = fields.Text(string='Sync Error', readonly=True)

    _sql_constraints = [
        ('technical_name_uniq', 'unique(technical_name)', 'Technical name must be unique!'),
    ]

    @api.depends('technical_name')
    def _compute_view_name(self):
        for rec in self:
            if rec.technical_name:
                # Ensure valid SQL identifier
                clean_name = re.sub(r'[^a-z0-9_]', '_', rec.technical_name.lower())
                rec.view_name = f'superset_{clean_name}'
            else:
                rec.view_name = False

    @api.depends('field_ids', 'include_all_fields', 'model_id')
    def _compute_column_count(self):
        for rec in self:
            if rec.include_all_fields and rec.model_id:
                rec.column_count = self.env['ir.model.fields'].search_count([
                    ('model_id', '=', rec.model_id.id),
                    ('ttype', 'not in', ['one2many', 'many2many', 'binary']),
                    ('store', '=', True),
                ])
            else:
                rec.column_count = len(rec.field_ids)

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            # Auto-generate technical name from model
            self.technical_name = self.model_id.model.replace('.', '_')
            self.name = self.model_id.name

    @api.model
    def _get_valid_field_types(self):
        """Field types that can be exposed to Superset"""
        return [
            'char', 'text', 'html',
            'integer', 'float', 'monetary',
            'boolean',
            'date', 'datetime',
            'selection',
            'many2one',  # Will be resolved to ID
        ]

    def _get_fields_for_view(self):
        """Get list of fields to include in the SQL view"""
        self.ensure_one()
        
        if self.source_type != 'model':
            return []
        
        if self.include_all_fields:
            fields = self.env['ir.model.fields'].search([
                ('model_id', '=', self.model_id.id),
                ('ttype', 'in', self._get_valid_field_types()),
                ('store', '=', True),
            ])
        else:
            fields = self.field_ids
        
        return fields

    def _generate_view_sql(self):
        """Generate SQL for the view"""
        self.ensure_one()
        
        if self.source_type == 'sql':
            return self.custom_sql
        
        if self.source_type != 'model' or not self.model_id:
            return False
        
        model = self.env[self.model_id.model]
        table_name = model._table
        
        fields_list = self._get_fields_for_view()
        if not fields_list:
            raise UserError(_('No fields selected for dataset'))
        
        # Build column list
        columns = ['id']  # Always include ID
        
        for field in fields_list:
            field_name = field.name
            field_type = field.ttype
            
            # Skip computed non-stored fields
            if not field.store:
                continue
            
            # Handle different field types
            if field_type == 'many2one':
                # Include the foreign key ID
                columns.append(field_name)
            elif field_type == 'selection':
                # Cast to text for better compatibility
                columns.append(f'{field_name}::text AS {field_name}')
            elif field_type in ('char', 'text', 'html'):
                columns.append(field_name)
            elif field_type in ('integer', 'float', 'monetary'):
                columns.append(field_name)
            elif field_type in ('date', 'datetime'):
                columns.append(field_name)
            elif field_type == 'boolean':
                columns.append(field_name)
            else:
                columns.append(field_name)
        
        # Add common metadata columns if they exist
        model_fields = [f.name for f in fields_list]
        for meta_col in ['create_date', 'write_date', 'create_uid', 'write_uid', 'company_id']:
            if meta_col not in model_fields and meta_col in model._fields:
                if model._fields[meta_col].store:
                    columns.append(meta_col)
        
        # Build SQL
        columns_sql = ',\n    '.join(columns)
        
        sql = f"""
-- Superset Analytics View: {self.name}
-- Generated by ipai_superset_connector
-- Model: {self.model_id.model}
-- Table: {table_name}

SELECT
    {columns_sql}
FROM {table_name}
WHERE active = true OR active IS NULL
"""
        
        return sql.strip()

    # =========================================================================
    # ACTIONS
    # =========================================================================
    
    def action_generate_sql(self):
        """Generate and preview the SQL view"""
        self.ensure_one()
        sql = self._generate_view_sql()
        self.view_sql = sql
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('SQL Generated'),
                'message': _('SQL view definition has been generated. Review in the SQL tab.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_create_view(self):
        """Create the SQL view in PostgreSQL"""
        self.ensure_one()
        
        if not self.view_sql:
            self.action_generate_sql()
        
        if not self.view_sql:
            raise UserError(_('No SQL to create view from'))
        
        # Validate view name
        if not self.view_name:
            raise UserError(_('No view name defined'))
        
        # Create or replace view
        view_sql = f"""
            CREATE OR REPLACE VIEW {self.view_name} AS
            {self.view_sql}
        """
        
        try:
            self.env.cr.execute(view_sql)
            self.view_created = True
            _logger.info('Created SQL view: %s', self.view_name)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('View Created'),
                    'message': _('SQL view "%s" created successfully') % self.view_name,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            _logger.error('Failed to create view %s: %s', self.view_name, str(e))
            raise UserError(_('Failed to create view: %s') % str(e))

    def action_drop_view(self):
        """Drop the SQL view"""
        self.ensure_one()
        
        if not self.view_name:
            return
        
        try:
            self.env.cr.execute(f'DROP VIEW IF EXISTS {self.view_name} CASCADE')
            self.view_created = False
            _logger.info('Dropped SQL view: %s', self.view_name)
        except Exception as e:
            _logger.warning('Failed to drop view %s: %s', self.view_name, str(e))

    def action_sync_to_superset(self):
        """Sync dataset to Superset"""
        self.ensure_one()
        
        if not self.connection_id.db_connection_id:
            raise UserError(_('Please create database connection in Superset first'))
        
        # Ensure view exists
        if self.source_type in ('model', 'view') and not self.view_created:
            self.action_create_view()
        
        try:
            conn = self.connection_id
            
            # Check if dataset exists
            if self.superset_dataset_id:
                # Refresh existing dataset
                conn.refresh_dataset(self.superset_dataset_id)
            else:
                # Create new dataset
                table_name = self.view_name if self.source_type in ('model', 'view') else self.technical_name
                result = conn.create_dataset(
                    table_name=table_name,
                    schema=conn.pg_schema or 'public',
                    database_id=conn.db_connection_id,
                )
                self.superset_dataset_id = result.get('id')
            
            self.write({
                'last_sync': fields.Datetime.now(),
                'sync_status': 'synced',
                'sync_error': False,
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Complete'),
                    'message': _('Dataset "%s" synced to Superset') % self.name,
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            self.write({
                'sync_status': 'error',
                'sync_error': str(e),
            })
            raise UserError(_('Sync failed: %s') % str(e))

    def action_open_in_superset(self):
        """Open dataset in Superset"""
        self.ensure_one()
        
        if not self.superset_dataset_id:
            raise UserError(_('Dataset not yet synced to Superset'))
        
        url = f'{self.connection_id.base_url}/explore/?dataset_type=table&dataset_id={self.superset_dataset_id}'
        
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    # =========================================================================
    # LIFECYCLE
    # =========================================================================
    
    def unlink(self):
        """Clean up SQL views when dataset is deleted"""
        for rec in self:
            rec.action_drop_view()
        return super().unlink()


class SupersetDatasetColumn(models.Model):
    """Extended column metadata for Superset datasets"""
    _name = 'superset.dataset.column'
    _description = 'Superset Dataset Column'
    _order = 'sequence, name'

    dataset_id = fields.Many2one(
        'superset.dataset',
        string='Dataset',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Column Name', required=True)
    label = fields.Char(string='Display Label')
    sequence = fields.Integer(default=10)
    
    column_type = fields.Selection([
        ('dimension', 'Dimension'),
        ('metric', 'Metric'),
        ('temporal', 'Temporal'),
    ], string='Column Type', default='dimension')
    
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'Datetime'),
    ], string='Data Type', default='string')
    
    # Metric configuration
    aggregation = fields.Selection([
        ('sum', 'Sum'),
        ('avg', 'Average'),
        ('count', 'Count'),
        ('count_distinct', 'Count Distinct'),
        ('min', 'Minimum'),
        ('max', 'Maximum'),
    ], string='Default Aggregation')
    
    # Formatting
    format_string = fields.Char(string='Format String')
    description = fields.Text(string='Description')
    
    # Visibility
    filterable = fields.Boolean(string='Filterable', default=True)
    groupable = fields.Boolean(string='Groupable', default=True)
