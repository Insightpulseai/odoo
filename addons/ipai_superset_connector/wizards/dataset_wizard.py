# -*- coding: utf-8 -*-
"""
Dataset Creation Wizard

Quick wizard to create Superset datasets from Odoo models.
"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SupersetDatasetWizard(models.TransientModel):
    _name = 'superset.dataset.wizard'
    _description = 'Create Superset Dataset'

    connection_id = fields.Many2one(
        'superset.connection',
        string='Superset Connection',
        required=True,
        default=lambda self: self._default_connection(),
    )
    
    model_id = fields.Many2one(
        'ir.model',
        string='Odoo Model',
        required=True,
        domain=[('transient', '=', False)],
    )
    
    name = fields.Char(string='Dataset Name')
    technical_name = fields.Char(string='Technical Name')
    
    include_all_fields = fields.Boolean(
        string='Include All Fields',
        default=True,
    )
    field_ids = fields.Many2many(
        'ir.model.fields',
        string='Selected Fields',
        domain="[('model_id', '=', model_id), ('ttype', 'not in', ['one2many', 'binary']), ('store', '=', True)]",
    )
    
    category = fields.Selection([
        ('sales', 'Sales & CRM'),
        ('finance', 'Finance & Accounting'),
        ('inventory', 'Inventory & Warehouse'),
        ('hr', 'Human Resources'),
        ('project', 'Project Management'),
        ('custom', 'Custom'),
    ], string='Category', default='custom')
    
    enable_rls = fields.Boolean(
        string='Enable Row-Level Security',
        default=True,
    )
    
    create_view = fields.Boolean(
        string='Create SQL View',
        default=True,
    )
    sync_to_superset = fields.Boolean(
        string='Sync to Superset',
        default=True,
    )

    @api.model
    def _default_connection(self):
        """Get default connection from settings"""
        param = self.env['ir.config_parameter'].sudo().get_param(
            'ipai_superset_connector.default_connection_id'
        )
        if param:
            return int(param)
        return self.env['superset.connection'].search([], limit=1).id

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            self.name = self.model_id.name
            self.technical_name = self.model_id.model.replace('.', '_')
            
            # Auto-detect category
            model_name = self.model_id.model
            if model_name.startswith('sale.'):
                self.category = 'sales'
            elif model_name.startswith('account.'):
                self.category = 'finance'
            elif model_name.startswith('stock.'):
                self.category = 'inventory'
            elif model_name.startswith('hr.'):
                self.category = 'hr'
            elif model_name.startswith('project.'):
                self.category = 'project'

    def action_create_dataset(self):
        """Create the dataset"""
        self.ensure_one()
        
        if not self.connection_id:
            raise UserError(_('Please select a Superset connection'))
        
        if not self.model_id:
            raise UserError(_('Please select an Odoo model'))
        
        # Check for existing
        existing = self.env['superset.dataset'].search([
            ('technical_name', '=', self.technical_name)
        ])
        if existing:
            raise UserError(_('Dataset with technical name "%s" already exists') % self.technical_name)
        
        # Create dataset
        dataset = self.env['superset.dataset'].create({
            'name': self.name or self.model_id.name,
            'technical_name': self.technical_name,
            'connection_id': self.connection_id.id,
            'source_type': 'model',
            'model_id': self.model_id.id,
            'include_all_fields': self.include_all_fields,
            'field_ids': [(6, 0, self.field_ids.ids)] if not self.include_all_fields else [],
            'category': self.category,
            'enable_rls': self.enable_rls,
        })
        
        # Create SQL view
        if self.create_view:
            dataset.action_generate_sql()
            dataset.action_create_view()
        
        # Sync to Superset
        if self.sync_to_superset and self.connection_id.db_connection_id:
            try:
                dataset.action_sync_to_superset()
            except Exception as e:
                # Don't fail if sync fails, dataset is still created locally
                pass
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'superset.dataset',
            'res_id': dataset.id,
            'view_mode': 'form',
            'target': 'current',
        }


class SupersetBulkDatasetWizard(models.TransientModel):
    """Create multiple datasets at once"""
    _name = 'superset.bulk.dataset.wizard'
    _description = 'Bulk Create Superset Datasets'

    connection_id = fields.Many2one(
        'superset.connection',
        string='Superset Connection',
        required=True,
    )
    
    preset = fields.Selection([
        ('sales', 'Sales Suite (sale.order, sale.order.line, res.partner)'),
        ('finance', 'Finance Suite (account.move, account.move.line, account.account)'),
        ('inventory', 'Inventory Suite (stock.quant, stock.move, product.product)'),
        ('hr', 'HR Suite (hr.employee, hr.department, hr.job)'),
        ('project', 'Project Suite (project.project, project.task)'),
        ('all', 'All Core Models'),
    ], string='Preset', default='all')
    
    create_analytics_views = fields.Boolean(
        string='Also Create Analytics Views',
        default=True,
    )

    def _get_preset_models(self):
        """Get model names for each preset"""
        presets = {
            'sales': ['sale.order', 'sale.order.line', 'res.partner', 'crm.lead', 'product.template'],
            'finance': ['account.move', 'account.move.line', 'account.account', 'account.journal', 'account.payment'],
            'inventory': ['stock.quant', 'stock.move', 'stock.picking', 'product.product', 'stock.warehouse'],
            'hr': ['hr.employee', 'hr.department', 'hr.job', 'hr.contract'],
            'project': ['project.project', 'project.task'],
        }
        
        if self.preset == 'all':
            all_models = []
            for models in presets.values():
                all_models.extend(models)
            return list(set(all_models))
        
        return presets.get(self.preset, [])

    def action_create_datasets(self):
        """Create all datasets for the preset"""
        self.ensure_one()
        
        model_names = self._get_preset_models()
        created = 0
        skipped = 0
        errors = []
        
        for model_name in model_names:
            # Check if model exists
            model = self.env['ir.model'].search([('model', '=', model_name)], limit=1)
            if not model:
                skipped += 1
                continue
            
            # Check if dataset already exists
            technical_name = model_name.replace('.', '_')
            existing = self.env['superset.dataset'].search([
                ('technical_name', '=', technical_name)
            ])
            if existing:
                skipped += 1
                continue
            
            try:
                dataset = self.env['superset.dataset'].create({
                    'name': model.name,
                    'technical_name': technical_name,
                    'connection_id': self.connection_id.id,
                    'source_type': 'model',
                    'model_id': model.id,
                    'include_all_fields': True,
                    'enable_rls': True,
                })
                dataset.action_generate_sql()
                dataset.action_create_view()
                created += 1
            except Exception as e:
                errors.append(f'{model_name}: {str(e)}')
        
        # Create analytics views if requested
        if self.create_analytics_views:
            AnalyticsView = self.env['superset.analytics.view']
            AnalyticsView.create_all_views()
        
        message = f'{created} datasets created, {skipped} skipped.'
        if errors:
            message += f'\n\nErrors:\n' + '\n'.join(errors)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Dataset Creation'),
                'message': message,
                'type': 'warning' if errors else 'success',
                'sticky': bool(errors),
            }
        }
