# -*- coding: utf-8 -*-
"""
Mattermost API v4 Client

This module provides a simple client for the Mattermost API.
It handles authentication and common API operations.
"""
import json
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Default timeout for API requests
DEFAULT_TIMEOUT = 30


class MattermostClient:
    """Simple Mattermost API v4 client."""

    def __init__(self, connector):
        """
        Initialize the client with a connector record.

        Args:
            connector: ipai.integration.connector record
        """
        self.connector = connector
        self.base_url = connector.base_url.rstrip("/")
        self.api_version = connector.api_version or "v4"
        self._token = None

    @property
    def api_url(self):
        """Get the full API URL."""
        return f"{self.base_url}/api/{self.api_version}"

    @property
    def token(self):
        """Get the authentication token."""
        if self._token is None:
            # Token should come from system parameters or secret ref
            # For now, use ir.config_parameter
            ICP = self.connector.env["ir.config_parameter"].sudo()
            self._token = ICP.get_param(
                f"ipai_mattermost.token_{self.connector.id}", default=""
            )
        return self._token

    def _headers(self):
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method, endpoint, data=None, params=None):
        """
        Make an API request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., /users/me)
            data: Request body (dict)
            params: Query parameters (dict)

        Returns:
            dict: Response JSON

        Raises:
            UserError: On API errors
        """
        url = f"{self.api_url}{endpoint}"

        try:
            response = requests.request(
                method,
                url,
                headers=self._headers(),
                json=data,
                params=params,
                timeout=DEFAULT_TIMEOUT,
            )

            if response.status_code >= 400:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", error_msg)
                except json.JSONDecodeError:
                    pass
                _logger.warning(
                    "Mattermost API error: %s %s -> %s: %s",
                    method,
                    endpoint,
                    response.status_code,
                    error_msg,
                )
                raise UserError(f"Mattermost API error: {error_msg}")

            if response.text:
                return response.json()
            return {}

        except requests.RequestException as e:
            _logger.error("Mattermost request failed: %s", e)
            raise UserError(f"Mattermost connection error: {e}")

    # System endpoints

    def ping(self):
        """Check if Mattermost is reachable."""
        result = self._request("GET", "/system/ping")
        return result.get("status") == "OK"

    def get_config(self):
        """Get server configuration (requires admin)."""
        return self._request("GET", "/config")

    # User endpoints

    def get_me(self):
        """Get current user info."""
        return self._request("GET", "/users/me")

    def get_user(self, user_id):
        """Get user by ID."""
        return self._request("GET", f"/users/{user_id}")

    # Team endpoints

    def get_teams(self):
        """Get all teams the user belongs to."""
        return self._request("GET", "/users/me/teams")

    def get_team(self, team_id):
        """Get team by ID."""
        return self._request("GET", f"/teams/{team_id}")

    # Channel endpoints

    def get_channels(self, team_id):
        """Get public channels for a team."""
        return self._request("GET", f"/teams/{team_id}/channels")

    def get_channel(self, channel_id):
        """Get channel by ID."""
        return self._request("GET", f"/channels/{channel_id}")

    def get_my_channels(self, team_id):
        """Get channels the user is a member of."""
        user = self.get_me()
        return self._request("GET", f"/users/{user['id']}/teams/{team_id}/channels")

    # Post endpoints

    def post_message(self, channel_id, message, props=None):
        """
        Post a message to a channel.

        Args:
            channel_id: Mattermost channel ID
            message: Message text (supports Markdown)
            props: Additional message properties (dict)

        Returns:
            dict: Created post data
        """
        data = {
            "channel_id": channel_id,
            "message": message,
        }
        if props:
            data["props"] = props

        result = self._request("POST", "/posts", data=data)

        # Log the message
        self.connector.env["ipai.mattermost.message"].log_outbound(
            self.connector, channel_id, message, result=result
        )

        return result

    def get_posts(self, channel_id, page=0, per_page=60):
        """Get posts from a channel."""
        return self._request(
            "GET",
            f"/channels/{channel_id}/posts",
            params={"page": page, "per_page": per_page},
        )

    # Webhook endpoints

    def create_incoming_webhook(self, channel_id, display_name, description=""):
        """Create an incoming webhook."""
        return self._request(
            "POST",
            "/hooks/incoming",
            data={
                "channel_id": channel_id,
                "display_name": display_name,
                "description": description,
            },
        )

    def create_outgoing_webhook(
        self, team_id, channel_id, trigger_words, callback_urls, display_name
    ):
        """Create an outgoing webhook."""
        return self._request(
            "POST",
            "/hooks/outgoing",
            data={
                "team_id": team_id,
                "channel_id": channel_id,
                "trigger_words": trigger_words,
                "callback_urls": callback_urls,
                "display_name": display_name,
            },
        )
