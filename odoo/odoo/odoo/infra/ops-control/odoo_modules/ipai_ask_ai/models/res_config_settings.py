# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # AI Backend Configuration
    ask_ai_endpoint = fields.Char(
        string='AI API Endpoint',
        config_parameter='ask_ai.endpoint',
        default='https://api.example.com/ask',
        help='The URL endpoint for the AI backend service',
    )
    ask_ai_api_key = fields.Char(
        string='AI API Key',
        config_parameter='ask_ai.api_key',
        help='API key for authentication with the AI service',
    )
    ask_ai_model = fields.Selection([
        ('claude-3-opus', 'Claude 3 Opus'),
        ('claude-3-sonnet', 'Claude 3 Sonnet'),
        ('claude-3-haiku', 'Claude 3 Haiku'),
        ('gpt-4', 'GPT-4'),
        ('gpt-4-turbo', 'GPT-4 Turbo'),
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        ('custom', 'Custom'),
    ], string='AI Model',
       config_parameter='ask_ai.model',
       default='claude-3-sonnet',
    )

    # Feature toggles
    ask_ai_enabled = fields.Boolean(
        string='Enable AI Copilot',
        config_parameter='ask_ai.enabled',
        default=True,
    )
    ask_ai_streaming = fields.Boolean(
        string='Enable Streaming Responses',
        config_parameter='ask_ai.streaming',
        default=True,
        help='Stream AI responses token by token for better UX',
    )
    ask_ai_auto_context = fields.Boolean(
        string='Auto-capture Context',
        config_parameter='ask_ai.auto_context',
        default=True,
        help='Automatically include current record/view context in prompts',
    )

    # Safety settings
    ask_ai_require_confirmation = fields.Boolean(
        string='Require Confirmation for Actions',
        config_parameter='ask_ai.require_confirmation',
        default=True,
        help='Show preview and require user confirmation before executing write actions',
    )
    ask_ai_allowed_models = fields.Text(
        string='Allowed Models for Actions',
        config_parameter='ask_ai.allowed_models',
        help='Comma-separated list of model names that AI can create/update. Leave empty for all models.',
    )
    ask_ai_blocked_models = fields.Text(
        string='Blocked Models for Actions',
        config_parameter='ask_ai.blocked_models',
        default='ir.model,ir.model.fields,ir.rule,ir.config_parameter,res.users',
        help='Comma-separated list of model names that AI cannot create/update',
    )

    # UI Settings
    ask_ai_panel_position = fields.Selection([
        ('right', 'Right Side'),
        ('left', 'Left Side'),
        ('float', 'Floating'),
    ], string='Panel Position',
       config_parameter='ask_ai.panel_position',
       default='right',
    )
    ask_ai_hotkey = fields.Char(
        string='Keyboard Shortcut',
        config_parameter='ask_ai.hotkey',
        default='Ctrl+Shift+A',
        help='Keyboard shortcut to open the AI Copilot',
    )

    @api.model
    def get_ask_ai_config(self):
        """Get AI config for frontend"""
        ICP = self.env['ir.config_parameter'].sudo()
        return {
            'enabled': ICP.get_param('ask_ai.enabled', 'True') == 'True',
            'endpoint': ICP.get_param('ask_ai.endpoint', ''),
            'model': ICP.get_param('ask_ai.model', 'claude-3-sonnet'),
            'streaming': ICP.get_param('ask_ai.streaming', 'True') == 'True',
            'auto_context': ICP.get_param('ask_ai.auto_context', 'True') == 'True',
            'require_confirmation': ICP.get_param('ask_ai.require_confirmation', 'True') == 'True',
            'panel_position': ICP.get_param('ask_ai.panel_position', 'right'),
            'hotkey': ICP.get_param('ask_ai.hotkey', 'Ctrl+Shift+A'),
        }
