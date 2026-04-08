# -*- coding: utf-8 -*-

import logging
import uuid

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class CopilotConversation(models.Model):
    _name = 'ipai.copilot.conversation'
    _description = 'Copilot Conversation'
    _inherit = ['mail.thread']
    _order = 'write_date desc, id desc'

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------
    name = fields.Char(
        required=True,
        default=lambda self: _('New Conversation'),
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        ondelete='cascade',
    )
    message_ids = fields.One2many(
        'ipai.copilot.message',
        'conversation_id',
        string='Messages',
    )
    state = fields.Selection(
        [('active', 'Active'), ('archived', 'Archived')],
        default='active',
        required=True,
        index=True,
        tracking=True,
    )
    context_model = fields.Char(
        string='Context Model',
        help='Odoo model name providing context for this conversation',
    )
    context_res_id = fields.Integer(
        string='Context Record ID',
        help='Record ID in the context model',
    )
    gateway_correlation_id = fields.Char(
        string='Gateway Correlation ID',
        readonly=True,
        copy=False,
        help='Links this conversation to the agent-platform gateway session',
    )
    message_count = fields.Integer(
        compute='_compute_message_count',
        string='Messages',
    )

    _sql_constraints = [
        ('gateway_correlation_id_uniq', 'unique(gateway_correlation_id)',
         'Gateway correlation ID must be unique.'),
    ]

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('message_ids')
    def _compute_message_count(self):
        for rec in self:
            rec.message_count = len(rec.message_ids)

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('gateway_correlation_id'):
                vals['gateway_correlation_id'] = str(uuid.uuid4())
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Action methods
    # -------------------------------------------------------------------------
    def action_archive(self):
        self.ensure_one()
        self.state = 'archived'

    def action_unarchive(self):
        self.ensure_one()
        self.state = 'active'
