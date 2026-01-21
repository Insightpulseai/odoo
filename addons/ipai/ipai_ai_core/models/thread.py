# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiAiThread(models.Model):
    _name = "ipai.ai.thread"
    _description = "IPAI AI Thread"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    name = fields.Char(default="AI Thread", compute="_compute_name", store=True)
    provider_id = fields.Many2one(
        "ipai.ai.provider",
        required=True,
        index=True,
        ondelete="restrict",
    )
    company_id = fields.Many2one(
        related="provider_id.company_id",
        store=True,
        index=True,
    )

    external_thread_id = fields.Char(
        index=True,
        help="External thread ID from the AI provider (e.g., Kapa thread ID).",
    )
    user_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        index=True,
    )

    message_ids = fields.One2many(
        "ipai.ai.message",
        "thread_id",
        string="Messages",
    )
    message_count = fields.Integer(
        compute="_compute_message_count",
        store=True,
    )

    state = fields.Selection(
        [
            ("active", "Active"),
            ("closed", "Closed"),
        ],
        default="active",
    )

    @api.depends("message_ids")
    def _compute_message_count(self):
        for rec in self:
            rec.message_count = len(rec.message_ids)

    @api.depends("message_ids", "message_ids.content")
    def _compute_name(self):
        for rec in self:
            first_msg = rec.message_ids.filtered(lambda m: m.role == "user")[:1]
            if first_msg:
                content = first_msg.content or ""
                rec.name = content[:50] + ("..." if len(content) > 50 else "")
            else:
                rec.name = f"AI Thread #{rec.id}" if rec.id else "New Thread"


class IpaiAiMessage(models.Model):
    _name = "ipai.ai.message"
    _description = "IPAI AI Message"
    _order = "create_date asc"

    thread_id = fields.Many2one(
        "ipai.ai.thread",
        required=True,
        index=True,
        ondelete="cascade",
    )
    role = fields.Selection(
        [
            ("user", "User"),
            ("assistant", "Assistant"),
            ("system", "System"),
        ],
        required=True,
    )
    content = fields.Text(required=True)

    # Provider metadata
    provider_latency_ms = fields.Integer(help="Response latency in milliseconds.")
    provider_status = fields.Char(help="HTTP status or provider-specific status code.")
    confidence = fields.Float(help="Confidence score from the provider (0.0 - 1.0).")
    tokens_used = fields.Integer(help="Number of tokens used for this message.")

    citation_ids = fields.One2many(
        "ipai.ai.citation",
        "message_id",
        string="Citations",
    )
    citation_count = fields.Integer(
        compute="_compute_citation_count",
        store=True,
    )

    @api.depends("citation_ids")
    def _compute_citation_count(self):
        for rec in self:
            rec.citation_count = len(rec.citation_ids)


class IpaiAiCitation(models.Model):
    _name = "ipai.ai.citation"
    _description = "IPAI AI Citation"
    _order = "rank asc, id asc"

    message_id = fields.Many2one(
        "ipai.ai.message",
        required=True,
        index=True,
        ondelete="cascade",
    )
    rank = fields.Integer(default=1)

    source_id = fields.Char(help="External source identifier from the provider.")
    title = fields.Char()
    url = fields.Char()
    snippet = fields.Text()
    score = fields.Float(help="Relevance score from the provider.")
