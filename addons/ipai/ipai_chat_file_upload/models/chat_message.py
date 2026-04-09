# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models


class ChatMessage(models.Model):
    _name = 'ipai.chat.message'
    _description = 'Chat Message'
    _order = 'create_date asc, id asc'

    session_id = fields.Many2one(
        'ipai.chat.session',
        string='Session',
        required=True,
        index=True,
        ondelete='cascade',
    )
    role = fields.Selection(
        [
            ('user', 'User'),
            ('assistant', 'Assistant'),
            ('system', 'System'),
        ],
        string='Role',
        required=True,
        index=True,
    )
    content = fields.Text(
        string='Content',
        required=True,
    )
    source_ids_snapshot = fields.Text(
        string='Eligible Source IDs',
        help='JSON array of source IDs eligible at response time',
    )
    provenance_summary = fields.Text(
        string='Provenance',
        help='Which sources were cited in this response',
    )
    latency_ms = fields.Integer(
        string='Latency (ms)',
        readonly=True,
    )
    external_request_id = fields.Char(
        string='External Request ID',
        index=True,
        readonly=True,
        copy=False,
    )

    @api.constrains('content')
    def _check_content_not_empty(self):
        for rec in self:
            if not (rec.content or '').strip():
                raise models.ValidationError(
                    'Message content cannot be empty.'
                )

    def get_source_snapshot_ids(self):
        """Parse the JSON snapshot back to a list of ints."""
        self.ensure_one()
        if not self.source_ids_snapshot:
            return []
        try:
            return json.loads(self.source_ids_snapshot)
        except (json.JSONDecodeError, TypeError):
            return []
