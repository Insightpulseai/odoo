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
    request_id = fields.Char(
        string='Request ID',
        help='Correlation ID from the agent-platform gateway',
        index=True,
    )

    attachment_ref_ids = fields.One2many(
        'ipai.copilot.attachment.ref',
        'message_id',
        string='Attachment References',
    )
    attachment_count = fields.Integer(
        compute='_compute_attachment_count',
        string='Attachment Count',
    )

    _sql_constraints = [
        ('request_id_uniq', 'unique(request_id)',
         'Request ID must be unique.'),
    ]

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('attachment_ref_ids')
    def _compute_attachment_count(self):
        for msg in self:
            msg.attachment_count = len(msg.attachment_ref_ids)

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

    def serialize_attachment_context(self):
        """Return attachment context for agent prompt injection."""
        self.ensure_one()
        refs = self.attachment_ref_ids.filtered(lambda r: r.ingestion_state == 'done')
        if not refs:
            return []
        return [
            {
                'filename': ref.filename,
                'mime_type': ref.mime_type,
                'snippet': ref.extracted_text or '',
                'token_estimate': ref.token_estimate,
            }
            for ref in refs
        ]
