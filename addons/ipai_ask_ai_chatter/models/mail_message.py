# -*- coding: utf-8 -*-
import re
import logging

from odoo import api, models
from odoo.tools import html2plaintext

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)

        ICP = self.env["ir.config_parameter"].sudo()
        enabled = ICP.get_param("ipai_ask_ai_chatter.enabled", "False") == "True"
        trigger = ICP.get_param("ipai_ask_ai_chatter.trigger", "@askai") or "@askai"

        if not enabled:
            return messages

        # Pattern: @askai <question> or @askai: <question>
        trig = re.escape(trigger)
        pattern = re.compile(rf"(^|\s){trig}\s*:?\s*(.+)$", re.IGNORECASE | re.DOTALL)

        for msg in messages:
            # Only process chatter comments on a record
            if not msg.model or not msg.res_id:
                continue
            if msg.message_type != "comment":
                continue

            plain = html2plaintext(msg.body or "").strip()
            m = pattern.search(plain)
            if not m:
                continue

            question = (m.group(2) or "").strip()
            if not question:
                continue

            _logger.info(
                "Ask AI triggered on %s,%s: %s",
                msg.model, msg.res_id, question[:100]
            )

            # Create request + enqueue job
            self.env["ipai.ask_ai_chatter.request"].sudo().create_from_message(
                msg, question
            )

        return messages
