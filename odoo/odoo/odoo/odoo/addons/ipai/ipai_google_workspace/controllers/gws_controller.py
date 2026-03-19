# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""HTTP endpoints for Google Workspace Add-on triggers.

Each endpoint receives a POST from Google with the event context,
verifies the Bearer token, delegates to the card builder, and returns
Card Service v1 JSON.

Routes:
    POST /ipai/gws/home      → Homepage card
    POST /ipai/gws/gmail     → Gmail contextual trigger
    POST /ipai/gws/calendar  → Calendar event open trigger
    POST /ipai/gws/drive     → Drive items selected trigger
    POST /ipai/gws/sheets    → Sheets file scope trigger
    POST /ipai/gws/action    → Button click / form submit handler
"""

import json
import logging

from odoo import http
from odoo.http import request, Response

from ..utils.auth import verify_google_token

_logger = logging.getLogger(__name__)


class GWSController(http.Controller):
    """Google Workspace Add-on HTTP controller."""

    def _verify_and_parse(self):
        """Extract Bearer token, verify it, parse JSON body.

        Returns:
            tuple: (event_data dict, token_claims dict)

        Raises:
            Returns HTTP 401 JSON response on auth failure.
        """
        auth_header = request.httprequest.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None, None

        token = auth_header[7:]
        project_number = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_gws.project_number", "")
        )
        if not project_number:
            _logger.error("ipai_gws.project_number not configured")
            return None, None

        try:
            claims = verify_google_token(token, project_number)
        except ValueError as exc:
            _logger.warning("GWS token verification failed: %s", exc)
            return None, None

        try:
            event_data = json.loads(request.httprequest.get_data(as_text=True))
        except (json.JSONDecodeError, Exception):
            event_data = {}

        return event_data, claims

    def _json_response(self, data, status=200):
        """Return a JSON response."""
        return Response(
            json.dumps(data),
            status=status,
            content_type="application/json",
        )

    def _error_401(self):
        """Return a 401 Unauthorized response."""
        return self._json_response({"error": "Unauthorized"}, status=401)

    def _is_enabled(self):
        """Check if GWS add-on is enabled in settings."""
        return (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_gws.enabled", "False")
        ) == "True"

    # ----- Trigger Endpoints -----

    @http.route("/ipai/gws/home", type="http", auth="none", methods=["POST"], csrf=False)
    def home(self):
        """Homepage trigger — shown when add-on icon is clicked."""
        if not self._is_enabled():
            return self._error_401()

        event_data, claims = self._verify_and_parse()
        if claims is None:
            return self._error_401()

        builder = request.env["ipai.gws.card.builder"].sudo()
        cards = builder._build_home_card(event_data)
        return self._json_response(cards)

    @http.route("/ipai/gws/gmail", type="http", auth="none", methods=["POST"], csrf=False)
    def gmail(self):
        """Gmail contextual trigger — shows sender info and actions."""
        if not self._is_enabled():
            return self._error_401()

        event_data, claims = self._verify_and_parse()
        if claims is None:
            return self._error_401()

        builder = request.env["ipai.gws.card.builder"].sudo()
        cards = builder._build_gmail_card(event_data)
        return self._json_response(cards)

    @http.route("/ipai/gws/calendar", type="http", auth="none", methods=["POST"], csrf=False)
    def calendar(self):
        """Calendar event open trigger — shows attendee info and related records."""
        if not self._is_enabled():
            return self._error_401()

        event_data, claims = self._verify_and_parse()
        if claims is None:
            return self._error_401()

        builder = request.env["ipai.gws.card.builder"].sudo()
        cards = builder._build_calendar_card(event_data)
        return self._json_response(cards)

    @http.route("/ipai/gws/drive", type="http", auth="none", methods=["POST"], csrf=False)
    def drive(self):
        """Drive items selected trigger — shows file actions."""
        if not self._is_enabled():
            return self._error_401()

        event_data, claims = self._verify_and_parse()
        if claims is None:
            return self._error_401()

        builder = request.env["ipai.gws.card.builder"].sudo()
        cards = builder._build_drive_card(event_data)
        return self._json_response(cards)

    @http.route("/ipai/gws/sheets", type="http", auth="none", methods=["POST"], csrf=False)
    def sheets(self):
        """Sheets file scope trigger — shows import/export actions."""
        if not self._is_enabled():
            return self._error_401()

        event_data, claims = self._verify_and_parse()
        if claims is None:
            return self._error_401()

        builder = request.env["ipai.gws.card.builder"].sudo()
        cards = builder._build_sheets_card(event_data)
        return self._json_response(cards)

    @http.route("/ipai/gws/action", type="http", auth="none", methods=["POST"], csrf=False)
    def action(self):
        """Action handler for button clicks and form submissions."""
        if not self._is_enabled():
            return self._error_401()

        event_data, claims = self._verify_and_parse()
        if claims is None:
            return self._error_401()

        builder = request.env["ipai.gws.card.builder"].sudo()
        result = builder._handle_action(event_data)
        return self._json_response(result)
