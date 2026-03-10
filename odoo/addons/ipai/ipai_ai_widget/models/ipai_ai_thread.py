# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
ipai.ai.thread — Record-scoped conversation thread.

Each thread is bound to a (user, record_model, record_id) triple so that
every user gets their own conversation history per Odoo record.
"""
from odoo import api, fields, models


class IpaiAiThread(models.Model):
    _name = "ipai.ai.thread"
    _description = "AI Conversation Thread"
    _order = "write_date desc"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        default=lambda self: self.env.user,
        index=True,
        ondelete="cascade",
    )
    record_model = fields.Char(string="Record Model", index=True)
    record_id = fields.Integer(string="Record ID")
    active = fields.Boolean(default=True)
    message_ids = fields.One2many(
        "ipai.ai.message",
        "thread_id",
        string="Messages",
    )

    @api.model
    def _get_or_create(self, user_id, record_model, record_id):
        """Return existing thread or create a new one."""
        thread = self.search(
            [
                ("user_id", "=", user_id),
                ("record_model", "=", record_model),
                ("record_id", "=", record_id),
            ],
            limit=1,
        )
        if not thread:
            thread = self.create(
                {
                    "user_id": user_id,
                    "record_model": record_model,
                    "record_id": record_id,
                }
            )
        return thread

    def _get_messages(self, limit=20):
        """Return last *limit* messages as a list of dicts."""
        self.ensure_one()
        messages = self.env["ipai.ai.message"].search(
            [("thread_id", "=", self.id)],
            order="create_date desc",
            limit=limit,
        )
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "preset_key": msg.preset_key or False,
                "trace_id": msg.trace_id or False,
                "create_date": fields.Datetime.to_string(msg.create_date),
            }
            for msg in reversed(messages)
        ]
