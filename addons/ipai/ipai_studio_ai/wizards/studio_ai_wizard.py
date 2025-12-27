# -*- coding: utf-8 -*-
"""
IPAI Studio AI - Command Wizard
===============================

Interactive wizard for processing and executing Studio AI commands.
"""

import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StudioAIWizard(models.TransientModel):
    """Wizard for interactive Studio AI commands."""

    _name = 'ipai.studio.ai.wizard'
    _description = 'Studio AI Command Wizard'

    # Input
    command = fields.Text(
        string='What would you like to do?',
        required=True,
        help='Describe what you want to create or modify in natural language.\n\n'
             'Examples:\n'
             '• Add a phone number field to contacts\n'
             '• Create a status dropdown on sales orders\n'
             '• When an invoice is confirmed, send an email',
    )

    # Context
    context_model_id = fields.Many2one(
        'ir.model',
        string='Current Model',
        help='If you want to add to a specific model, select it here',
    )

    # Analysis results
    state = fields.Selection([
        ('input', 'Input'),
        ('analysis', 'Analysis'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], default='input', string='State')

    command_type = fields.Selection([
        ('field', 'Field Creation'),
        ('view', 'View Modification'),
        ('automation', 'Automation'),
        ('report', 'Report'),
        ('unknown', 'Unknown'),
    ], string='Detected Type', readonly=True)

    confidence = fields.Float(
        string='Confidence',
        readonly=True,
        digits=(3, 2),
    )

    analysis_json = fields.Text(
        string='Analysis JSON',
        readonly=True,
    )

    message = fields.Html(
        string='Analysis',
        readonly=True,
    )

    is_ready = fields.Boolean(
        string='Ready to Execute',
        readonly=True,
    )

    # Field-specific
    field_name = fields.Char(string='Field Name')
    field_label = fields.Char(string='Field Label')
    field_type = fields.Selection([
        ('char', 'Text'),
        ('text', 'Long Text'),
        ('html', 'Rich Text'),
        ('integer', 'Integer'),
        ('float', 'Decimal'),
        ('monetary', 'Monetary'),
        ('boolean', 'Checkbox'),
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        ('selection', 'Selection'),
        ('many2one', 'Many2One'),
        ('one2many', 'One2Many'),
        ('many2many', 'Many2Many'),
        ('binary', 'Binary/File'),
    ], string='Field Type')
    field_required = fields.Boolean(string='Required')
    target_model_id = fields.Many2one(
        'ir.model',
        string='Target Model',
    )
    selection_options = fields.Text(
        string='Selection Options',
        help='One option per line',
    )
    relation_model_id = fields.Many2one(
        'ir.model',
        string='Related Model',
    )

    # Result
    result_message = fields.Html(
        string='Result',
        readonly=True,
    )
    created_field_id = fields.Many2one(
        'ir.model.fields',
        string='Created Field',
        readonly=True,
    )
    history_id = fields.Many2one(
        'ipai.studio.ai.history',
        string='History Record',
        readonly=True,
    )

    def action_analyze(self):
        """Analyze the command."""
        self.ensure_one()

        context = {}
        if self.context_model_id:
            context['model'] = self.context_model_id.model

        service = self.env['ipai.studio.ai.service']
        result = service.process_command(self.command, context)

        # Log to history
        history = self.env['ipai.studio.ai.history'].log_command(self.command, result)

        analysis = result.get('analysis', {})

        # Convert message to HTML
        message_html = result.get('message', '').replace('\n', '<br/>')
        message_html = message_html.replace('**', '<strong>').replace('**', '</strong>')
        message_html = message_html.replace('`', '<code>').replace('`', '</code>')

        vals = {
            'state': 'analysis' if result.get('ready') else 'confirm',
            'command_type': result.get('type'),
            'confidence': result.get('confidence', 0.0),
            'analysis_json': json.dumps(analysis),
            'message': message_html,
            'is_ready': result.get('ready', False),
            'history_id': history.id,
        }

        # Populate field-specific values
        if result.get('type') == 'field':
            vals.update({
                'field_name': analysis.get('field_name', ''),
                'field_label': analysis.get('field_label', ''),
                'field_type': analysis.get('field_type', 'char'),
                'field_required': analysis.get('required', False),
            })
            if analysis.get('model_id'):
                vals['target_model_id'] = analysis['model_id']
            if analysis.get('selection_options'):
                vals['selection_options'] = '\n'.join([
                    opt[1] for opt in analysis['selection_options']
                ])
            if analysis.get('relation_model'):
                rel_model = self.env['ir.model'].search([
                    ('model', '=', analysis['relation_model'])
                ], limit=1)
                if rel_model:
                    vals['relation_model_id'] = rel_model.id

        self.write(vals)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ipai.studio.ai.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_execute(self):
        """Execute the analyzed command."""
        self.ensure_one()

        if self.command_type == 'field':
            return self._execute_field_creation()
        elif self.command_type == 'automation':
            return self._execute_automation_creation()
        else:
            raise UserError(_("This command type is not yet supported for automatic execution."))

    def _execute_field_creation(self):
        """Execute field creation."""
        if not self.target_model_id:
            raise UserError(_("Please select a target model."))
        if not self.field_name:
            raise UserError(_("Please specify a field name."))

        # Build analysis from wizard values
        analysis = {
            'model_id': self.target_model_id.id,
            'field_name': self.field_name,
            'field_label': self.field_label or self.field_name.replace('x_', '').replace('_', ' ').title(),
            'field_type': self.field_type,
            'required': self.field_required,
        }

        # Parse selection options
        if self.field_type == 'selection' and self.selection_options:
            options = []
            for line in self.selection_options.strip().split('\n'):
                line = line.strip()
                if line:
                    key = line.lower().replace(' ', '_')
                    options.append((key, line))
            analysis['selection_options'] = options

        # Set relation model
        if self.relation_model_id:
            analysis['relation_model'] = self.relation_model_id.model

        # Execute
        service = self.env['ipai.studio.ai.service']
        result = service.execute_field_creation(analysis)

        if result.get('success'):
            self.write({
                'state': 'done',
                'result_message': '<p class="text-success">%s</p>' % result.get('message', 'Field created!'),
                'created_field_id': result.get('field_id'),
            })
            if self.history_id:
                self.history_id.mark_executed(
                    result.get('message', ''),
                    field_id=result.get('field_id'),
                )
        else:
            self.write({
                'state': 'error',
                'result_message': '<p class="text-danger">Error: %s</p>' % result.get('error', 'Unknown error'),
            })
            if self.history_id:
                self.history_id.mark_failed(result.get('error', 'Unknown error'))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ipai.studio.ai.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _execute_automation_creation(self):
        """Open automation wizard with pre-filled values."""
        analysis = json.loads(self.analysis_json or '{}')

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Create Automation'),
            'res_model': 'base.automation',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_name': analysis.get('description', '')[:100],
                'default_model_id': analysis.get('model_id'),
                'default_trigger': analysis.get('trigger', 'on_create'),
            },
        }

        if self.history_id:
            self.history_id.mark_executed('Opened automation wizard')

        return action

    def action_cancel(self):
        """Cancel the command."""
        if self.history_id:
            self.history_id.mark_cancelled()
        return {'type': 'ir.actions.act_window_close'}

    def action_new_command(self):
        """Start a new command."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ipai.studio.ai.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
