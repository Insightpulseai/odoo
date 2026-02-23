# -*- coding: utf-8 -*-
import hmac
import hashlib
import logging
import json

from odoo import http, SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)


def _verify_mailgun_signature(timestamp, token, signature, signing_key):
    """Verify Mailgun webhook signature."""
    if not (timestamp and token and signature and signing_key):
        return False
    msg = f"{timestamp}{token}".encode("utf-8")
    key = signing_key.encode("utf-8")
    digest = hmac.new(key, msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)


class MailgunWebhookController(http.Controller):

    @http.route(['/mailgun/inbound'], type='http', auth='public', methods=['POST'], csrf=False)
    def mailgun_inbound(self, **kw):
        """Inbound messages from Mailgun -> create/update Odoo records."""
        env = request.env
        params = request.params

        signing_key = env['ir.config_parameter'].sudo().get_param('ipai_mailgun.webhook_signing_key')
        timestamp = params.get('timestamp')
        token = params.get('token')
        signature = params.get('signature')

        if signing_key and not _verify_mailgun_signature(timestamp, token, signature, signing_key):
            _logger.warning("Mailgun inbound: invalid signature")
            return http.Response("invalid signature", status=403)

        recipient = params.get('recipient', '')
        sender = params.get('from', '')
        subject = params.get('subject', '')
        body_plain = params.get('stripped-text', '') or params.get('body-plain', '')
        body_html = params.get('body-html', '')
        message_id = params.get('Message-Id') or params.get('message-id')

        _logger.info("Mailgun inbound: recipient=%s sender=%s subject=%s", recipient, sender, subject)

        # Basic routing by alias
        local_part = recipient.split('@')[0].lower() if '@' in recipient else recipient.lower()

        with env.cr.savepoint():
            env = env.sudo(SUPERUSER_ID)

            support_alias = env['ir.config_parameter'].sudo().get_param('ipai_mailgun.support_alias', 'support')
            sales_alias = env['ir.config_parameter'].sudo().get_param('ipai_mailgun.sales_alias', 'sales')
            projects_alias = env['ir.config_parameter'].sudo().get_param('ipai_mailgun.projects_alias', 'projects')

            if local_part == support_alias:
                # Create support channel message (no helpdesk dependency)
                channel = env['mail.channel'].search([('name', '=', 'Support Inbox')], limit=1)
                if not channel:
                    channel = env['mail.channel'].create({
                        'name': 'Support Inbox',
                        'description': 'Inbound support emails from Mailgun',
                        'channel_type': 'channel',
                    })
                channel.message_post(
                    body=body_html or body_plain,
                    subject=subject,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    email_from=sender,
                )
            elif local_part == sales_alias:
                # Create CRM lead
                lead = env['crm.lead'].create({
                    'name': subject or f"Lead from {sender}",
                    'description': body_plain or body_html,
                    'email_from': sender,
                })
                lead.message_post(
                    body=body_html or body_plain,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    email_from=sender,
                )
            elif local_part == projects_alias:
                # Generic project inbox -> create a task in default project (if configured)
                project = env['project.project'].search([], limit=1)
                if project:
                    task = env['project.task'].create({
                        'name': subject or f"Email task from {sender}",
                        'description': body_plain or body_html,
                        'project_id': project.id,
                    })
                    task.message_post(
                        body=body_html or body_plain,
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment',
                        email_from=sender,
                    )
            else:
                # Fallback: log and drop or create generic mail.message
                _logger.info("Mailgun inbound: unhandled alias: %s", local_part)

        return http.Response("ok", status=200)

    @http.route(['/mailgun/events'], type='json', auth='public', methods=['POST'], csrf=False)
    def mailgun_events(self, **kw):
        """Mailgun events: delivered, opened, clicked, bounced."""
        env = request.env
        data = request.jsonrequest or {}
        event = data.get('event')
        message_id = data.get('Message-Id') or data.get('message-id')
        recipient = data.get('recipient')
        reason = data.get('reason') or data.get('description')

        signing_key = env['ir.config_parameter'].sudo().get_param('ipai_mailgun.webhook_signing_key')
        signature = data.get('signature')
        timestamp = data.get('timestamp')
        token = data.get('token')

        if signing_key and not _verify_mailgun_signature(timestamp, token, signature, signing_key):
            _logger.warning("Mailgun events: invalid signature")
            return {"status": "error", "reason": "invalid signature"}

        _logger.info("Mailgun event: %s message_id=%s recipient=%s reason=%s",
                     event, message_id, recipient, reason)

        # Example: store basic tracking on mail.mail or mail.message
        env = env.sudo(SUPERUSER_ID)
        if message_id:
            mail = env['mail.mail'].search([('message_id', '=', message_id)], limit=1)
            if mail:
                mail.write({'ipai_mailgun_last_event': event})

        return {"status": "ok"}
