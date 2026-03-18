# -*- coding: utf-8 -*-
from odoo import fields, models


class IpaiAiThread(models.Model):
    _name = "ipai.ai.thread"
    _description = "AI Conversation Thread"
    _order = "create_date desc"

    provider_id = fields.Many2one(
        "ipai.ai.provider",
        string="Provider",
        required=True,
        ondelete="restrict",
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        default=lambda self: self.env.user,
    )
    message_ids = fields.One2many(
        "ipai.ai.message",
        "thread_id",
        string="Messages",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
