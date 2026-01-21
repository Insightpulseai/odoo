# -*- coding: utf-8 -*-
"""
Copilot Hub Controllers

Provides API endpoints for the frontend OWL component to retrieve
hub configuration and handle authentication.
"""
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class CopilotHubController(http.Controller):
    """Controller for Copilot Hub API endpoints."""

    @http.route(
        "/ipai/copilot/hub/config",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def get_hub_config(self):
        """
        Get the hub configuration for the current user.

        Returns:
            dict: Hub configuration including URL, embed mode, and user context
        """
        ICP = request.env["ir.config_parameter"].sudo()
        user = request.env.user

        return {
            "url": ICP.get_param(
                "ipai.copilot.hub_url",
                default="https://ops.insightpulseai.net",
            ),
            "embed_mode": ICP.get_param(
                "ipai.copilot.hub_embed_mode",
                default="iframe",
            ),
            "show_toolbar": ICP.get_param(
                "ipai.copilot.hub_show_toolbar",
                default="True",
            )
            == "True",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "company_id": user.company_id.id,
                "company_name": user.company_id.name,
            },
        }

    @http.route(
        "/ipai/copilot/hub/ping",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def ping(self):
        """Health check endpoint for the hub controller."""
        return request.make_json_response(
            {"status": "ok", "module": "ipai_copilot_hub"},
        )

    @http.route(
        "/ipai/copilot/hub/context",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def get_odoo_context(self, **kwargs):
        """
        Get Odoo context data to pass to the external hub.

        This can be used to pass session info, active record context,
        or other Odoo state to the external application.

        Args:
            kwargs: Optional context parameters from frontend

        Returns:
            dict: Odoo context data for the hub
        """
        user = request.env.user
        company = user.company_id

        context_data = {
            "odoo_session": {
                "uid": user.id,
                "user_name": user.name,
                "user_email": user.email,
                "company_id": company.id,
                "company_name": company.name,
                "lang": user.lang or "en_US",
                "tz": user.tz or "UTC",
            },
            "odoo_base_url": request.httprequest.host_url.rstrip("/"),
        }

        # Include active model/record if provided
        if kwargs.get("active_model"):
            context_data["active_model"] = kwargs["active_model"]
        if kwargs.get("active_id"):
            context_data["active_id"] = kwargs["active_id"]
        if kwargs.get("active_ids"):
            context_data["active_ids"] = kwargs["active_ids"]

        return context_data
