# -*- coding: utf-8 -*-
from odoo import fields, models


class IpaiAiMessage(models.Model):
    _name = "ipai.ai.message"
    _description = "AI Conversation Message"
    _order = "create_date asc"

    thread_id = fields.Many2one(
        "ipai.ai.thread",
        string="Thread",
        required=True,
        ondelete="cascade",
    )
    role = fields.Selection(
        [
            ("user", "User"),
            ("assistant", "Assistant"),
            ("system", "System"),
        ],
        required=True,
        default="user",
    )
    content = fields.Text(required=True)
    confidence = fields.Float(default=0.0)
    provider_latency_ms = fields.Integer(
        string="Provider Latency (ms)", default=0
    )
    citation_ids = fields.One2many(
        "ipai.ai.citation",
        "message_id",
        string="Citations",
    )
