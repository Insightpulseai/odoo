import logging
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)

# Session TTL for Google → Odoo session mapping
SESSION_TTL_MINUTES = 10


class GoogleWorkspaceSession(models.Model):
    """Maps Google Identity to Odoo sessions for the Workspace Add-on.

    Dual-identity protocol:
    1. Google ID token verified (signature, iss/exp/aud/email_verified)
    2. Odoo user looked up by email
    3. Short-lived session token returned for subsequent API calls
    """

    _name = 'google.workspace.session'
    _description = 'Google Workspace Add-on Session'
    _order = 'create_date desc'

    google_sub = fields.Char(
        string='Google Subject ID',
        required=True,
        index=True,
    )
    google_email = fields.Char(
        string='Google Email',
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Odoo User',
        ondelete='cascade',
    )
    session_token = fields.Char(
        string='Session Token',
        readonly=True,
    )
    expires_at = fields.Datetime(
        string='Expires At',
        readonly=True,
    )
    is_active = fields.Boolean(
        string='Active',
        compute='_compute_is_active',
    )

    _sql_constraints = [
        ('google_sub_uniq', 'unique(google_sub)',
         'Each Google account maps to one session.'),
    ]

    @api.depends('expires_at')
    def _compute_is_active(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.is_active = rec.expires_at and rec.expires_at > now

    @api.model
    def create_or_refresh_session(self, google_sub, google_email):
        """Create or refresh a session for a verified Google identity.

        Returns session_token for use in subsequent API calls.
        Raises AccessDenied if no matching Odoo user exists.
        """
        import secrets

        # Find matching Odoo user by email
        user = self.env['res.users'].sudo().search([
            ('login', '=', google_email),
        ], limit=1)

        if not user:
            # Try partner email as fallback
            user = self.env['res.users'].sudo().search([
                ('partner_id.email', '=', google_email),
            ], limit=1)

        if not user:
            _logger.warning(
                'Google Workspace: no Odoo user for %s', google_email
            )
            raise AccessDenied(
                _('No Odoo account linked to %s. Contact your administrator.',
                  google_email)
            )

        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(minutes=SESSION_TTL_MINUTES)

        session = self.sudo().search([
            ('google_sub', '=', google_sub),
        ], limit=1)

        if session:
            session.sudo().write({
                'session_token': token,
                'expires_at': expires,
                'user_id': user.id,
                'google_email': google_email,
            })
        else:
            session = self.sudo().create({
                'google_sub': google_sub,
                'google_email': google_email,
                'user_id': user.id,
                'session_token': token,
                'expires_at': expires,
            })

        return {
            'session_token': token,
            'expires_at': fields.Datetime.to_string(expires),
            'user_name': user.name,
        }

    @api.model
    def validate_session(self, session_token):
        """Validate a session token and return the user.

        Returns res.users recordset or raises AccessDenied.
        """
        session = self.sudo().search([
            ('session_token', '=', session_token),
            ('expires_at', '>', fields.Datetime.now()),
        ], limit=1)

        if not session:
            raise AccessDenied(_('Invalid or expired session.'))

        return session.user_id

    @api.autovacuum
    def _gc_expired_sessions(self):
        """Garbage-collect expired sessions (runs via cron)."""
        expired = self.sudo().search([
            ('expires_at', '<', fields.Datetime.now()),
        ])
        count = len(expired)
        expired.unlink()
        if count:
            _logger.info('GC: removed %d expired Google Workspace sessions', count)
