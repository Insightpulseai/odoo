import hashlib
import logging
import secrets
from datetime import datetime, timedelta

from odoo import _, http
from odoo.http import request
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)

SESSION_TTL_HOURS = 24


class MailPluginBridgeController(http.Controller):
    """JSON-RPC endpoints for the InsightPulseAI Gmail add-on."""

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    @http.route(
        "/ipai/mail_plugin/session",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def session(self, email=None, api_key=None, **kw):
        """Validate user credentials and return a session token.

        The add-on stores this token and sends it as a Bearer header
        on subsequent requests.
        """
        if not email or not api_key:
            return {"error": "email and api_key are required"}

        user = (
            request.env["res.users"]
            .sudo()
            .search([("login", "=", email)], limit=1)
        )
        if not user:
            _logger.warning("Mail plugin login attempt for unknown user: %s", email)
            return {"error": "invalid credentials"}

        # Odoo 19 stores API keys via res.users.api_key; validate
        if not user._check_credentials(api_key, env={"interactive": False}):
            _logger.warning("Mail plugin invalid API key for user: %s", email)
            return {"error": "invalid credentials"}

        # Create session
        token = secrets.token_urlsafe(48)
        expires_at = datetime.utcnow() + timedelta(hours=SESSION_TTL_HOURS)

        request.env["ipai.mail.plugin.session"].sudo().create(
            {
                "user_id": user.id,
                "token": hashlib.sha256(token.encode()).hexdigest(),
                "expires_at": expires_at,
                "active": True,
            }
        )

        return {
            "token": token,
            "expires_at": expires_at.isoformat(),
            "user_name": user.name,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _authenticate_token(self):
        """Extract and validate Bearer token. Returns res.users or raises."""
        auth_header = request.httprequest.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise AccessDenied(_("Missing or invalid Authorization header"))

        raw_token = auth_header[7:]
        hashed = hashlib.sha256(raw_token.encode()).hexdigest()

        session = (
            request.env["ipai.mail.plugin.session"]
            .sudo()
            .search(
                [
                    ("token", "=", hashed),
                    ("active", "=", True),
                    ("expires_at", ">", datetime.utcnow()),
                ],
                limit=1,
            )
        )
        if not session:
            raise AccessDenied(_("Session expired or invalid"))

        return session.user_id

    def _record_url(self, model, res_id):
        """Build a web client URL for a record."""
        base = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return f"{base}/web#model={model}&id={res_id}&view_type=form"

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    @http.route(
        "/ipai/mail_plugin/context",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def context(self, sender_email=None, subject=None, **kw):
        """Look up a partner by email and return related records."""
        user = self._authenticate_token()
        env = request.env(user=user)

        partner = env["res.partner"].search(
            [("email", "=ilike", sender_email)], limit=1
        )

        result = {
            "partner": None,
            "leads": [],
            "tickets": [],
            "tasks": [],
        }

        if not partner:
            return result

        result["partner"] = {
            "id": partner.id,
            "name": partner.name,
            "email": partner.email,
            "phone": partner.phone or "",
            "company": partner.parent_id.name if partner.parent_id else "",
            "url": self._record_url("res.partner", partner.id),
        }

        # CRM leads / opportunities
        leads = env["crm.lead"].search(
            [("partner_id", "=", partner.id)],
            limit=10,
            order="create_date desc",
        )
        result["leads"] = [
            {
                "id": lead.id,
                "name": lead.name,
                "stage": lead.stage_id.name if lead.stage_id else "",
                "url": self._record_url("crm.lead", lead.id),
            }
            for lead in leads
        ]

        # Project tasks (used as tickets)
        tasks = env["project.task"].search(
            [("partner_id", "=", partner.id)],
            limit=10,
            order="create_date desc",
        )
        result["tasks"] = [
            {
                "id": task.id,
                "name": task.name,
                "stage": task.stage_id.name if task.stage_id else "",
                "state": task.stage_id.name if task.stage_id else "",
                "url": self._record_url("project.task", task.id),
            }
            for task in tasks
        ]

        return result

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    @http.route(
        "/ipai/mail_plugin/actions/create_lead",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def create_lead(self, sender_email=None, name=None, **kw):
        """Create a CRM lead from email metadata."""
        user = self._authenticate_token()
        env = request.env(user=user)

        partner = env["res.partner"].search(
            [("email", "=ilike", sender_email)], limit=1
        )

        vals = {
            "name": name or f"Lead from {sender_email}",
            "email_from": sender_email,
            "type": "lead",
        }
        if partner:
            vals["partner_id"] = partner.id

        lead = env["crm.lead"].create(vals)
        _logger.info("Mail plugin created lead %s for %s", lead.id, sender_email)

        return {
            "id": lead.id,
            "name": lead.name,
            "url": self._record_url("crm.lead", lead.id),
        }

    @http.route(
        "/ipai/mail_plugin/actions/create_ticket",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def create_ticket(self, sender_email=None, name=None, **kw):
        """Create a project task (ticket) from email metadata."""
        user = self._authenticate_token()
        env = request.env(user=user)

        partner = env["res.partner"].search(
            [("email", "=ilike", sender_email)], limit=1
        )

        vals = {
            "name": name or f"Ticket from {sender_email}",
        }
        if partner:
            vals["partner_id"] = partner.id

        task = env["project.task"].create(vals)
        _logger.info("Mail plugin created task %s for %s", task.id, sender_email)

        return {
            "id": task.id,
            "name": task.name,
            "url": self._record_url("project.task", task.id),
        }

    @http.route(
        "/ipai/mail_plugin/actions/log_note",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def log_note(self, sender_email=None, partner_id=None, body=None, **kw):
        """Post a note to a partner's chatter."""
        user = self._authenticate_token()
        env = request.env(user=user)

        if partner_id:
            partner = env["res.partner"].browse(int(partner_id))
        else:
            partner = env["res.partner"].search(
                [("email", "=ilike", sender_email)], limit=1
            )

        if not partner.exists():
            return {"error": "partner not found"}

        partner.message_post(
            body=body or f"Note logged from Gmail for {sender_email}",
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )
        _logger.info(
            "Mail plugin logged note to partner %s for %s",
            partner.id,
            sender_email,
        )

        return {
            "ok": True,
            "partner_id": partner.id,
        }
