# -*- coding: utf-8 -*-
"""
Ask AI Channel Extension

Extends discuss.channel to support AI chat functionality.
"""

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class DiscussChannel(models.Model):
    """
    Extension of discuss.channel for AI chat support.
    """
    _inherit = "discuss.channel"

    is_ai_channel = fields.Boolean(
        string="Is AI Channel",
        default=False,
        help="Whether this channel is an AI assistant chat",
    )

    @api.model
    def create_ai_draft_channel(self):
        """
        Create or get the AI draft channel for the current user.

        This is called from the frontend when opening the Ask AI widget.

        Returns:
            dict: Channel data for the frontend
        """
        ai_service = self.env["ipai.ask.ai.service"]
        channel = ai_service.get_or_create_ai_channel()

        return {
            "id": channel.id,
            "name": channel.name,
            "uuid": channel.uuid,
            "is_ai_channel": True,
        }

    def _get_ai_response(self, message_body, context=None):
        """
        Get AI response for a message.

        Args:
            message_body: The user's message text
            context: Optional context dict

        Returns:
            str: AI response message
        """
        ai_service = self.env["ipai.ask.ai.service"]
        result = ai_service.process_query(message_body, context)

        return result.get("response", _("I couldn't process that request."))

    def ai_message_post(self, message_body, context=None):
        """
        Post a message and get AI response.

        Args:
            message_body: User's message
            context: Optional context

        Returns:
            dict: Result with user message ID and AI response
        """
        self.ensure_one()

        # Post user message
        user_message = self.message_post(
            body=message_body,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )

        # Get AI response
        ai_response = self._get_ai_response(message_body, context)

        # Get AI partner
        ai_partner = self.env.ref("ipai_ask_ai.partner_ask_ai", raise_if_not_found=False)
        if not ai_partner:
            ai_partner = self.env["res.partner"].sudo().search([
                ("email", "=", "ai@insightpulseai.net")
            ], limit=1)

        # Post AI response
        ai_message = self.sudo().message_post(
            body=ai_response,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            author_id=ai_partner.id if ai_partner else False,
        )

        return {
            "user_message_id": user_message.id,
            "ai_message_id": ai_message.id,
            "ai_response": ai_response,
        }
