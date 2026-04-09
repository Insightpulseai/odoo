# -*- coding: utf-8 -*-

import json
import logging

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SocialPost(models.Model):
    """Social media post with scheduling, publishing, and analytics."""
    _name = 'ipai.social.post'
    _description = 'Social Media Post'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc, id desc'

    message = fields.Text(
        required=True,
        tracking=True,
        help='Post content. Platform character limits apply at publish time.',
    )
    image_ids = fields.Many2many(
        'ir.attachment',
        string='Images',
        help='Images to include with the post',
    )
    account_ids = fields.Many2many(
        'ipai.social.account',
        string='Accounts',
        required=True,
        help='Social accounts to publish to',
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )

    # Scheduling
    scheduled_date = fields.Datetime(
        index=True,
        tracking=True,
    )
    published_date = fields.Datetime(readonly=True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('scheduled', 'Scheduled'),
            ('posting', 'Posting'),
            ('posted', 'Posted'),
            ('failed', 'Failed'),
        ],
        default='draft',
        required=True,
        index=True,
        tracking=True,
    )
    failure_reason = fields.Text(readonly=True)

    # Analytics
    click_count = fields.Integer(readonly=True)
    impression_count = fields.Integer(readonly=True)
    engagement_count = fields.Integer(readonly=True)

    # External references (per-account publish results)
    publish_result_ids = fields.One2many(
        'ipai.social.post.result',
        'post_id',
        string='Publish Results',
    )

    # UTM tracking
    utm_campaign_id = fields.Many2one('utm.campaign', string='Campaign')
    utm_source_id = fields.Many2one('utm.source', string='Source')

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def action_schedule(self):
        for post in self:
            if not post.scheduled_date:
                raise UserError('Set a scheduled date before scheduling.')
            if not post.account_ids:
                raise UserError('Select at least one social account.')
            post.state = 'scheduled'

    def action_post_now(self):
        for post in self:
            if not post.account_ids:
                raise UserError('Select at least one social account.')
            post.state = 'scheduled'
            post.scheduled_date = fields.Datetime.now()
        self._enqueue_publish()

    def action_reset_draft(self):
        self.filtered(lambda p: p.state in ('failed', 'scheduled')).write({
            'state': 'draft',
            'failure_reason': False,
        })

    # -------------------------------------------------------------------------
    # Cron + queue_job
    # -------------------------------------------------------------------------

    @api.model
    def _cron_process_scheduled(self):
        """Find due scheduled posts and enqueue publishing."""
        posts = self.search([
            ('state', '=', 'scheduled'),
            ('scheduled_date', '<=', fields.Datetime.now()),
        ], limit=50)
        if posts:
            posts._enqueue_publish()

    def _enqueue_publish(self):
        for post in self:
            post.with_delay(
                channel='root.social_marketing',
                description='Publish social post #%d' % post.id,
            )._do_publish()

    def _do_publish(self):
        """Publish to all accounts. Called via queue_job."""
        self.ensure_one()
        self.state = 'posting'
        errors = []
        for account in self.account_ids:
            try:
                result = self._publish_to_platform(account)
                self.env['ipai.social.post.result'].create({
                    'post_id': self.id,
                    'account_id': account.id,
                    'external_id': result.get('id', ''),
                    'external_url': result.get('url', ''),
                    'status': 'success',
                })
            except Exception as e:
                _logger.warning(
                    'Social post %d failed on %s: %s',
                    self.id, account.name, e,
                )
                errors.append('%s: %s' % (account.name, str(e)[:200]))
                self.env['ipai.social.post.result'].create({
                    'post_id': self.id,
                    'account_id': account.id,
                    'status': 'failed',
                    'error_message': str(e)[:500],
                })

        if errors and len(errors) == len(self.account_ids):
            self.write({
                'state': 'failed',
                'failure_reason': '\n'.join(errors),
            })
        else:
            self.write({
                'state': 'posted',
                'published_date': fields.Datetime.now(),
                'failure_reason': '\n'.join(errors) if errors else False,
            })
            for account in self.account_ids:
                account.last_post_at = fields.Datetime.now()

    # -------------------------------------------------------------------------
    # Platform-specific publishing
    # -------------------------------------------------------------------------

    def _publish_to_platform(self, account):
        """Dispatch to platform-specific publisher.

        Returns dict with 'id' and 'url' of the published post.
        """
        self.ensure_one()
        method = getattr(
            self, '_publish_to_%s' % account.platform, None,
        )
        if not method:
            raise UserError(
                'Publishing to %s is not yet supported.' % account.platform
            )
        return method(account)

    def _publish_to_linkedin(self, account):
        """Publish to LinkedIn using the Share API v2."""
        access_token = account._get_credential('access_token')
        org_id = account._get_credential('organization_id')
        if not access_token or not org_id:
            raise UserError(
                'LinkedIn credentials not configured. '
                'Set ipai_social.linkedin.%d.access_token and '
                'ipai_social.linkedin.%d.organization_id '
                'in System Parameters.' % (account.id, account.id)
            )
        author = 'urn:li:organization:%s' % org_id
        payload = {
            'author': author,
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {'text': self.message},
                    'shareMediaCategory': 'NONE',
                },
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC',
            },
        }
        resp = requests.post(
            'https://api.linkedin.com/v2/ugcPosts',
            headers={
                'Authorization': 'Bearer %s' % access_token,
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0',
            },
            json=payload,
            timeout=30,
        )
        if resp.status_code not in (200, 201):
            raise UserError('LinkedIn API error: %s' % resp.text[:300])
        data = resp.json()
        post_id = data.get('id', '')
        return {
            'id': post_id,
            'url': 'https://www.linkedin.com/feed/update/%s' % post_id,
        }

    def _publish_to_facebook(self, account):
        """Publish to Facebook Page using Graph API."""
        access_token = account._get_credential('access_token')
        page_id = account._get_credential('page_id')
        if not access_token or not page_id:
            raise UserError(
                'Facebook credentials not configured. '
                'Set ipai_social.facebook.%d.access_token and '
                'ipai_social.facebook.%d.page_id '
                'in System Parameters.' % (account.id, account.id)
            )
        resp = requests.post(
            'https://graph.facebook.com/v19.0/%s/feed' % page_id,
            data={
                'message': self.message,
                'access_token': access_token,
            },
            timeout=30,
        )
        if resp.status_code != 200:
            raise UserError('Facebook API error: %s' % resp.text[:300])
        data = resp.json()
        post_id = data.get('id', '')
        return {
            'id': post_id,
            'url': 'https://www.facebook.com/%s' % post_id,
        }

    def _publish_to_twitter(self, account):
        """Publish to X (Twitter) using v2 API."""
        bearer_token = account._get_credential('bearer_token')
        if not bearer_token:
            raise UserError(
                'X (Twitter) credentials not configured. '
                'Set ipai_social.twitter.%d.bearer_token '
                'in System Parameters.' % account.id
            )
        resp = requests.post(
            'https://api.twitter.com/2/tweets',
            headers={
                'Authorization': 'Bearer %s' % bearer_token,
                'Content-Type': 'application/json',
            },
            json={'text': self.message[:280]},
            timeout=30,
        )
        if resp.status_code not in (200, 201):
            raise UserError('X API error: %s' % resp.text[:300])
        data = resp.json().get('data', {})
        tweet_id = data.get('id', '')
        return {
            'id': tweet_id,
            'url': 'https://x.com/i/status/%s' % tweet_id,
        }

    def _publish_to_instagram(self, account):
        raise UserError(
            'Instagram publishing requires Business API setup. '
            'Configure via Facebook Graph API for Instagram.'
        )

    def _publish_to_tiktok(self, account):
        raise UserError(
            'TikTok publishing is not yet implemented.'
        )

    # -------------------------------------------------------------------------
    # Analytics cron
    # -------------------------------------------------------------------------

    @api.model
    def _cron_fetch_analytics(self):
        """Fetch engagement metrics for recently published posts."""
        recent = self.search([
            ('state', '=', 'posted'),
            ('published_date', '>=',
             fields.Datetime.subtract(fields.Datetime.now(), days=7)),
        ], limit=100)
        for post in recent:
            try:
                post._fetch_analytics()
            except Exception:
                _logger.debug(
                    'Analytics fetch failed for post %d', post.id,
                    exc_info=True,
                )

    def _fetch_analytics(self):
        """Override per-platform to fetch metrics. Stub for now."""
        pass


class SocialPostResult(models.Model):
    """Per-account publish result for a social post."""
    _name = 'ipai.social.post.result'
    _description = 'Social Post Publish Result'
    _order = 'create_date desc'

    post_id = fields.Many2one(
        'ipai.social.post',
        required=True,
        ondelete='cascade',
        index=True,
    )
    account_id = fields.Many2one(
        'ipai.social.account',
        required=True,
        ondelete='cascade',
    )
    external_id = fields.Char(string='External Post ID')
    external_url = fields.Char(string='Post URL')
    status = fields.Selection(
        [('success', 'Success'), ('failed', 'Failed')],
        required=True,
    )
    error_message = fields.Text()
