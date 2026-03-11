# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
ipai.ai.message — Individual prompt/response in a conversation thread.
"""
from odoo import fields, models

_ROLES = [
    ("user", "User"),
    ("assistant", "Assistant"),
    ("system", "System"),
]


class IpaiAiMessage(models.Model):
    _name = "ipai.ai.message"
    _description = "AI Conversation Message"
    _order = "create_date asc"

    thread_id = fields.Many2one(
        "ipai.ai.thread",
        string="Thread",
        required=True,
        ondelete="cascade",
        index=True,
    )
    role = fields.Selection(
        _ROLES,
        string="Role",
        required=True,
    )
    content = fields.Text(string="Content")
    preset_key = fields.Char(string="Preset Key")
    trace_id = fields.Char(string="Trace ID")
