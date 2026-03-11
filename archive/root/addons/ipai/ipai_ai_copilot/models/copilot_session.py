"""
ipai.copilot.session — Per-user conversation session.

Max 50 turns (100 messages total). Stored in Odoo DB as JSON (not pgvector).
Sessions are per-user and cannot be shared across users.
History is trimmed to 50 turns on every append to prevent unbounded growth.
"""
import json
from odoo import models, fields, api


class IpaiCopilotSession(models.Model):
    _name = "ipai.copilot.session"
    _description = "IPAI Copilot Conversation Session"
    _order = "write_date desc"

    name = fields.Char(default="Copilot Session")
    user_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user.id,
        required=True,
        index=True,
        ondelete="cascade",
    )
    history_json = fields.Text(default="[]")  # JSON list of {role, content}
    active = fields.Boolean(default=True)

    @api.model
    def _get_or_create(self, session_id=None):
        """Return existing session for this user or create a new one."""
        if session_id:
            try:
                session = self.browse(int(session_id))
                if session.exists() and session.user_id == self.env.user:
                    return session
            except (ValueError, TypeError):
                pass
        # Create new session for this user
        return self.create({"user_id": self.env.user.id})

    def _get_history(self, max_turns=50):
        """Return up to max_turns of conversation history."""
        try:
            history = json.loads(self.history_json or "[]")
        except (json.JSONDecodeError, TypeError):
            history = []
        # Each turn is a pair: one user + one assistant message
        # max_turns * 2 = max messages
        return history[-(max_turns * 2):]

    def _append(self, role, content):
        """Append a message to history with FIFO truncation at 50 turns."""
        try:
            history = json.loads(self.history_json or "[]")
        except (json.JSONDecodeError, TypeError):
            history = []
        history.append({"role": role, "content": content})
        # Trim to 50 turns (100 messages)
        if len(history) > 100:
            history = history[-100:]
        self.sudo().write({"history_json": json.dumps(history)})
