# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CopilotMessage(models.Model):
    _name = 'ipai.copilot.message'
    _description = 'Copilot Message'
    _order = 'create_date asc, id asc'

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------
    conversation_id = fields.Many2one(
        'ipai.copilot.conversation',
        string='Conversation',
        required=True,
        ondelete='cascade',
        index=True,
    )
    role = fields.Selection(
        [
            ('user', 'User'),
            ('assistant', 'Assistant'),
            ('system', 'System'),
            ('tool', 'Tool'),
        ],
        required=True,
        index=True,
    )
    content = fields.Text(
        required=True,
    )
    tool_calls = fields.Json(
        string='Tool Calls',
        help='Structured tool call data from the agent response',
    )
    latency_ms = fields.Integer(
        string='Latency (ms)',
        help='Response time from the gateway in milliseconds',
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'copilot_message_attachment_rel',
        'message_id',
        'attachment_id',
        string='Attachments',
        help='Files attached to this message',
    )
    request_id = fields.Char(
        string='Request ID',
        help='Correlation ID from the agent-platform gateway',
        index=True,
    )

    _sql_constraints = [
        ('request_id_uniq', 'unique(request_id)',
         'Request ID must be unique.'),
    ]

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------
    @api.constrains('content')
    def _check_content_not_empty(self):
        for rec in self:
            if not (rec.content or '').strip():
                raise models.ValidationError(
                    'Message content cannot be empty.'
                )
