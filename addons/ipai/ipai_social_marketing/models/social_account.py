# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

PLATFORM_SELECTION = [
    ('facebook', 'Facebook'),
    ('instagram', 'Instagram'),
    ('linkedin', 'LinkedIn'),
    ('twitter', 'X (Twitter)'),
    ('tiktok', 'TikTok'),
]


class SocialAccount(models.Model):
    """Social media account with API credentials for posting.

    API credentials are resolved from ir.config_parameter at runtime.
    Keys follow the pattern: ipai_social.<platform>.<field>
    e.g. ipai_social.linkedin.access_token
    """
    _name = 'ipai.social.account'
    _description = 'Social Media Account'
    _order = 'platform, name'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    platform = fields.Selection(
        PLATFORM_SELECTION,
        required=True,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    active = fields.Boolean(default=True)
    account_url = fields.Char(
        string='Profile URL',
        help='Public profile URL for this account',
    )
    last_post_at = fields.Datetime(readonly=True)
    post_count = fields.Integer(
        compute='_compute_post_count',
        string='Posts',
    )

    # API configuration — credential param keys, not raw secrets
    api_config_prefix = fields.Char(
        compute='_compute_api_config_prefix',
        string='Config Key Prefix',
        help='ir.config_parameter prefix for this account credentials',
    )

    @api.depends('platform')
    def _compute_api_config_prefix(self):
        for rec in self:
            rec.api_config_prefix = (
                'ipai_social.%s.%s' % (rec.platform, rec.id)
                if rec.platform and rec._origin.id
                else ''
            )

    def _compute_post_count(self):
        for rec in self:
            rec.post_count = self.env['ipai.social.post'].search_count([
                ('account_ids', 'in', rec.id),
            ])

    def _get_credential(self, key):
        """Get a credential from ir.config_parameter.

        Args:
            key: credential suffix, e.g. 'access_token', 'page_id'

        Returns the parameter value or empty string.
        """
        self.ensure_one()
        param_key = 'ipai_social.%s.%s.%s' % (self.platform, self.id, key)
        return self.env['ir.config_parameter'].sudo().get_param(
            param_key, ''
        )

    def action_view_posts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Posts — %s' % self.name,
            'res_model': 'ipai.social.post',
            'view_mode': 'list,form,calendar',
            'domain': [('account_ids', 'in', self.id)],
            'context': {'default_account_ids': [(6, 0, [self.id])]},
        }
