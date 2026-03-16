# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
import json
import logging

_logger = logging.getLogger(__name__)


class AskAIConversation(models.Model):
    """AI Copilot Conversation Session"""
    _name = 'ask.ai.conversation'
    _description = 'AI Copilot Conversation'
    _order = 'create_date desc'
    _rec_name = 'title'

    title = fields.Char(
        string='Title',
        compute='_compute_title',
        store=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        required=True,
        index=True,
    )
    message_ids = fields.One2many(
        'ask.ai.message',
        'conversation_id',
        string='Messages',
    )
    message_count = fields.Integer(
        string='Messages',
        compute='_compute_message_count',
    )

    # Context when conversation started
    context_model = fields.Char(
        string='Context Model',
        help='The Odoo model active when conversation started',
    )
    context_res_id = fields.Integer(
        string='Context Record ID',
        help='The record ID active when conversation started',
    )
    context_view_type = fields.Selection([
        ('form', 'Form'),
        ('list', 'List'),
        ('kanban', 'Kanban'),
        ('calendar', 'Calendar'),
        ('pivot', 'Pivot'),
        ('graph', 'Graph'),
        ('search', 'Search'),
        ('other', 'Other'),
    ], string='View Type')
    context_action_id = fields.Many2one(
        'ir.actions.act_window',
        string='Context Action',
    )

    # Conversation settings
    mode = fields.Selection([
        ('ask', 'Ask'),
        ('do', 'Do'),
        ('explain', 'Explain'),
    ], string='Mode', default='ask')

    state = fields.Selection([
        ('active', 'Active'),
        ('archived', 'Archived'),
    ], string='State', default='active')

    # Metadata
    last_message_date = fields.Datetime(
        string='Last Message',
        compute='_compute_last_message_date',
        store=True,
    )

    @api.depends('message_ids', 'message_ids.content')
    def _compute_title(self):
        for conv in self:
            first_user_msg = conv.message_ids.filtered(
                lambda m: m.role == 'user'
            )[:1]
            if first_user_msg:
                content = first_user_msg.content or ''
                conv.title = content[:50] + ('...' if len(content) > 50 else '')
            else:
                conv.title = _('New Conversation')

    @api.depends('message_ids')
    def _compute_message_count(self):
        for conv in self:
            conv.message_count = len(conv.message_ids)

    @api.depends('message_ids.create_date')
    def _compute_last_message_date(self):
        for conv in self:
            if conv.message_ids:
                conv.last_message_date = max(conv.message_ids.mapped('create_date'))
            else:
                conv.last_message_date = conv.create_date

    def action_archive(self):
        """Archive the conversation"""
        self.write({'state': 'archived'})

    def action_unarchive(self):
        """Unarchive the conversation"""
        self.write({'state': 'active'})

    @api.model
    def get_or_create_conversation(self, context_data=None):
        """Get existing active conversation or create new one"""
        context_data = context_data or {}

        # Look for recent active conversation (within last hour)
        recent = self.search([
            ('user_id', '=', self.env.uid),
            ('state', '=', 'active'),
            ('create_date', '>=', fields.Datetime.subtract(
                fields.Datetime.now(), hours=1
            )),
        ], limit=1, order='create_date desc')

        if recent:
            return recent

        # Create new conversation
        return self.create({
            'user_id': self.env.uid,
            'context_model': context_data.get('model'),
            'context_res_id': context_data.get('res_id'),
            'context_view_type': context_data.get('view_type'),
            'context_action_id': context_data.get('action_id'),
            'mode': context_data.get('mode', 'ask'),
        })

    def add_message(self, role, content, metadata=None):
        """Add a message to the conversation"""
        self.ensure_one()
        return self.env['ask.ai.message'].create({
            'conversation_id': self.id,
            'role': role,
            'content': content,
            'metadata': json.dumps(metadata) if metadata else False,
        })

    def get_messages_for_api(self, limit=20):
        """Get messages formatted for AI API"""
        self.ensure_one()
        messages = self.message_ids.sorted('create_date')[-limit:]
        return [{
            'role': msg.role,
            'content': msg.content,
        } for msg in messages]
