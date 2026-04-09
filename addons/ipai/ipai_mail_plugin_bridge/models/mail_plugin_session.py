import hashlib
import logging
from datetime import datetime

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class MailPluginSession(models.Model):
    """Tracks authenticated sessions for the Gmail add-on bridge.

    Tokens are stored as SHA-256 hashes. The raw token is only ever
    held by the client (Gmail add-on) and never persisted server-side.
    """

    _name = "ipai.mail.plugin.session"
    _description = "Mail Plugin Session"
    _order = "expires_at desc"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        ondelete="cascade",
        index=True,
    )
    token = fields.Char(
        string="Token Hash",
        required=True,
        index=True,
        help="SHA-256 hash of the session token.",
    )
    expires_at = fields.Datetime(
        string="Expires At",
        required=True,
        index=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _sql_constraints = [
        (
            "token_uniq",
            "unique(token)",
            "Session token hash must be unique.",
        ),
    ]

    @api.model
    def validate_token(self, raw_token):
        """Validate a raw token and return the associated user or False.

        Args:
            raw_token: The plaintext token sent by the client.

        Returns:
            res.users recordset (single) or False.
        """
        hashed = hashlib.sha256(raw_token.encode()).hexdigest()
        session = self.sudo().search(
            [
                ("token", "=", hashed),
                ("active", "=", True),
                ("expires_at", ">", datetime.utcnow()),
            ],
            limit=1,
        )
        if session:
            return session.user_id
        return False

    @api.model
    def _gc_expired_sessions(self):
        """Cron-callable garbage collection for expired sessions."""
        expired = self.sudo().search(
            [("expires_at", "<", datetime.utcnow())]
        )
        count = len(expired)
        if count:
            expired.write({"active": False})
            _logger.info("Mail plugin: deactivated %d expired sessions", count)
        return True
