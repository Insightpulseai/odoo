# -*- coding: utf-8 -*-
from odoo import fields, models


class IpaiAiCitation(models.Model):
    _name = "ipai.ai.citation"
    _description = "AI Message Citation"
    _order = "rank"

    message_id = fields.Many2one(
        "ipai.ai.message",
        string="Message",
        required=True,
        ondelete="cascade",
    )
    rank = fields.Integer(required=True)
    title = fields.Char()
    url = fields.Char(string="URL")
    snippet = fields.Text()
    score = fields.Float(default=0.0)
