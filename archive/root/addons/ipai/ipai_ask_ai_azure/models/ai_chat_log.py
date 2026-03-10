# (c) 2026 InsightPulse AI — License LGPL-3.0-or-later
from odoo import fields, models


class IpaiAskAiChatLog(models.Model):
    _name = "ipai.ask.ai.chat.log"
    _description = "Ask AI Azure Chat Audit Log"
    _order = "create_date desc"
    _log_access = True

    user_id = fields.Many2one("res.users", string="User", index=True)
    conversation_id = fields.Char(index=True)
    trace_id = fields.Char(index=True)
    prompt_len = fields.Integer()
    outcome = fields.Char(index=True)
    latency_ms = fields.Integer()
    model = fields.Char()
