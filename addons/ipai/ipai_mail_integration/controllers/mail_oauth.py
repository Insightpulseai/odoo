# -*- coding: utf-8 -*-
"""
IPAI Mail OAuth Controllers

Handles OAuth callbacks for Gmail and Outlook integration.
"""

import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IpaiMailOAuthController(http.Controller):
    """OAuth callback controller for mail integrations."""

    @http.route("/ipai/mail/oauth/callback", type="http", auth="user", website=True)
    def oauth_callback(self, code=None, state=None, error=None, **kwargs):
        """Handle OAuth callback from Google or Microsoft."""
        if error:
            _logger.warning("OAuth error: %s", error)
            return request.redirect("/web#action=mail.action_discuss")

        if not code:
            _logger.warning("No authorization code received")
            return request.redirect("/web#action=mail.action_discuss")

        # Process the authorization code
        # In production, exchange code for tokens and store them
        _logger.info("OAuth callback received with code (length: %d)", len(code))

        # TODO: Exchange code for access/refresh tokens
        # TODO: Store tokens securely
        # TODO: Configure mail server with OAuth

        return request.redirect("/web#action=mail.action_discuss")

    @http.route("/ipai/mail/oauth/google/authorize", type="http", auth="user")
    def google_authorize(self, **kwargs):
        """Initiate Google OAuth flow."""
        Provider = request.env["ipai.mail.oauth.provider"].sudo()
        provider = Provider.search([("provider_type", "=", "google")], limit=1)

        if not provider:
            return request.redirect("/web?error=no_google_provider")

        base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        redirect_uri = f"{base_url}/ipai/mail/oauth/callback"

        auth_url = provider.get_authorization_url(redirect_uri, state="google")
        return request.redirect(auth_url)

    @http.route("/ipai/mail/oauth/microsoft/authorize", type="http", auth="user")
    def microsoft_authorize(self, **kwargs):
        """Initiate Microsoft OAuth flow."""
        Provider = request.env["ipai.mail.oauth.provider"].sudo()
        provider = Provider.search([("provider_type", "=", "microsoft")], limit=1)

        if not provider:
            return request.redirect("/web?error=no_microsoft_provider")

        base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        redirect_uri = f"{base_url}/ipai/mail/oauth/callback"

        auth_url = provider.get_authorization_url(redirect_uri, state="microsoft")
        return request.redirect(auth_url)
