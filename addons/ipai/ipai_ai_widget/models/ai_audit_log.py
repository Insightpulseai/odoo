# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
ipai.ai.audit.log — Minimal audit log for Ask AI requests.

Stores request metadata ONLY — no raw prompt text, no response text.
This ensures no sensitive data is persisted in the Odoo database.

Records are written via sudo() in the controller so they always land
even if the calling user has restricted model access.
"""
from odoo import fields, models

_OUTCOMES = [
    ("success", "Success"),
    ("bridge_url_not_configured", "URL Not Configured"),
    ("ai_key_not_configured", "Key Not Configured"),
    ("bridge_timeout", "Timeout"),
    ("bridge_error", "Bridge Error"),
    ("prompt_required", "Empty Prompt"),
]


class IpaiAiAuditLog(models.Model):
    _name = "ipai.ai.audit.log"
    _description = "IPAI AI Request Audit Log"
    _order = "create_date desc"
    _rec_name = "trace_id"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        readonly=True,
        index=True,
        ondelete="set null",
    )
    record_model = fields.Char(string="Record Model", readonly=True, index=True)
    record_id = fields.Integer(string="Record ID", readonly=True)
    trace_id = fields.Char(string="Trace ID", readonly=True, index=True)
    outcome = fields.Selection(
        _OUTCOMES,
        string="Outcome",
        readonly=True,
        index=True,
    )
    latency_ms = fields.Integer(string="Latency (ms)", readonly=True)
    error_code = fields.Char(string="Error Code", readonly=True)
    prompt_len = fields.Integer(
        string="Prompt Length (chars)",
        readonly=True,
        help="Character count of the prompt — stored for volume analytics, NOT the content.",
    )
    # Deliberate: NO prompt, response, or body fields.
    # Security boundary: raw AI content must not persist in Odoo DB.
