# -*- coding: utf-8 -*-
import uuid

from odoo import api, fields, models


class ChatSession(models.Model):
    _name = 'ipai.chat.session'
    _description = 'Chat Session'
    _order = 'write_date desc, id desc'

    name = fields.Char(
        string='Title',
        required=True,
        default=lambda self: 'New Chat',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Owner',
        required=True,
        default=lambda self: self.env.uid,
        index=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        ondelete='cascade',
    )
    state = fields.Selection(
        [('active', 'Active'), ('archived', 'Archived')],
        string='State',
        default='active',
        index=True,
    )
    source_ids = fields.One2many(
        'ipai.chat.source',
        'session_id',
        string='Sources',
    )
    chat_message_ids = fields.One2many(
        'ipai.chat.message',
        'session_id',
        string='Chat Messages',
    )
    external_session_id = fields.Char(
        string='External Session ID',
        readonly=True,
        copy=False,
        index=True,
    )
    message_count = fields.Integer(
        string='Messages',
        compute='_compute_message_count',
    )
    source_count = fields.Integer(
        string='Sources',
        compute='_compute_source_count',
    )
    eligible_source_count = fields.Integer(
        string='Eligible Sources',
        compute='_compute_source_count',
    )

    @api.depends('chat_message_ids')
    def _compute_message_count(self):
        for rec in self:
            rec.message_count = len(rec.chat_message_ids)

    @api.depends('source_ids', 'source_ids.status', 'source_ids.active')
    def _compute_source_count(self):
        for rec in self:
            sources = rec.with_context(active_test=False).source_ids
            rec.source_count = len(sources)
            rec.eligible_source_count = len(
                sources.filtered(lambda s: s.active and s.status == 'indexed')
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('external_session_id'):
                vals['external_session_id'] = str(uuid.uuid4())
        return super().create(vals_list)

    def action_archive(self):
        self.write({'state': 'archived'})

    def action_unarchive(self):
        self.write({'state': 'active'})

    def get_eligible_sources(self):
        """Return sources eligible for grounded chat."""
        return self.source_ids.filtered(
            lambda s: s.active and s.status == 'indexed'
        )
