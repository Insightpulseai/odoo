# -*- coding: utf-8 -*-

import logging
import time

from odoo import models

_logger = logging.getLogger(__name__)


class DiscussChannelCopilot(models.Model):
    """Extend discuss.channel to route DM messages to Azure Foundry Copilot.

    When a user sends a DM in a chat channel where the IPAI Copilot partner
    is a member, the message is forwarded to the configured Foundry agent.
    The agent's response is posted back into the channel as the copilot.

    This only activates when:
      - channel_type == 'chat' (direct messages)
      - IPAI Copilot partner is in the channel
      - Foundry integration is enabled in settings
      - The message author is NOT the copilot itself (prevent loops)
    """

    _inherit = "discuss.channel"

    def _message_post_after_hook(self, message, msg_vals):
        """Intercept messages in copilot DM channels."""
        result = super()._message_post_after_hook(message, msg_vals)

        # Only trigger for chat-type channels (1-on-1 DMs)
        if self.channel_type != "chat":
            return result

        # Only trigger for user comments, not system notifications
        if msg_vals.get("message_type") != "comment":
            return result

        copilot_partner = self._copilot_get_partner()
        if not copilot_partner:
            return result

        # Check if copilot is a member of this channel
        channel_partners = self.channel_member_ids.mapped("partner_id")
        if copilot_partner not in channel_partners:
            return result

        # Don't respond to our own messages (prevent loops)
        author_id = msg_vals.get("author_id")
        if author_id == copilot_partner.id:
            return result

        # Rate limit: skip if last copilot message was < 2s ago
        last_copilot_msg = self.env["mail.message"].search(
            [
                ("res_id", "=", self.id),
                ("model", "=", "discuss.channel"),
                ("author_id", "=", copilot_partner.id),
            ],
            order="date desc",
            limit=1,
        )
        if last_copilot_msg:
            elapsed = time.time() - last_copilot_msg.date.timestamp()
            if elapsed < 2.0:
                _logger.debug("Copilot rate-limited (%.1fs since last)", elapsed)
                return result

        self._copilot_handle_message(message, copilot_partner)
        return result

    def _copilot_get_partner(self):
        """Get the IPAI Copilot partner record, or None if not seeded."""
        try:
            return self.env.ref("ipai_odoo_copilot.partner_copilot")
        except ValueError:
            return None

    def _copilot_handle_message(self, message, copilot_partner):
        """Route a user message to Azure Foundry and post the response."""
        service = self.env["ipai.foundry.service"]
        settings = service._get_settings()

        if not settings["enabled"]:
            _logger.debug("Copilot disabled — skipping message %s", message.id)
            return

        # Extract plain text from message body
        body = message.body
        if hasattr(message, "body_plaintext") and message.body_plaintext:
            body = message.body_plaintext
        else:
            # Strip HTML tags for plain text
            import re  # noqa: PLC0415
            body = re.sub(r"<[^>]+>", "", body or "").strip()

        if not body:
            return

        # Build conversation context from recent messages
        history = self._copilot_build_history(copilot_partner)

        # Call Foundry for response
        user_id = message.author_id.id if message.author_id else None
        response_text = service.chat_completion(
            user_message=body,
            history=history,
            user_id=user_id,
        )

        if not response_text:
            _logger.warning(
                "Copilot got empty response for message %s", message.id
            )
            return

        # Post response as copilot partner
        self.with_context(mail_create_nosubscribe=True).sudo().message_post(
            body=response_text,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            author_id=copilot_partner.id,
        )

    def _copilot_build_history(self, copilot_partner, limit=10):
        """Build conversation history from recent channel messages.

        Returns list of dicts: [{"role": "user"|"assistant", "content": str}]
        """
        import re  # noqa: PLC0415

        messages = self.env["mail.message"].search(
            [
                ("res_id", "=", self.id),
                ("model", "=", "discuss.channel"),
                ("message_type", "=", "comment"),
            ],
            order="date desc",
            limit=limit,
        )
        history = []
        for msg in reversed(messages):
            body = msg.body or ""
            if hasattr(msg, "body_plaintext") and msg.body_plaintext:
                text = msg.body_plaintext
            else:
                text = re.sub(r"<[^>]+>", "", body).strip()
            if not text:
                continue
            role = "assistant" if msg.author_id == copilot_partner else "user"
            history.append({"role": role, "content": text})
        return history
