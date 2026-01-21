# -*- coding: utf-8 -*-
"""
Focalboard API Client

This module provides a simple client for the Focalboard API.
"""
import json
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class FocalboardClient:
    """Simple Focalboard REST API client."""

    def __init__(self, connector):
        """
        Initialize the client with a connector record.

        Args:
            connector: ipai.integration.connector record
        """
        self.connector = connector
        self.base_url = connector.base_url.rstrip("/")
        self._token = None

    @property
    def api_url(self):
        """Get the full API URL."""
        return f"{self.base_url}/api/v2"

    @property
    def token(self):
        """Get the authentication token."""
        if self._token is None:
            ICP = self.connector.env["ir.config_parameter"].sudo()
            self._token = ICP.get_param(
                f"ipai_focalboard.token_{self.connector.id}", default=""
            )
        return self._token

    def _headers(self):
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method, endpoint, data=None, params=None):
        """
        Make an API request.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body (dict)
            params: Query parameters (dict)

        Returns:
            dict or list: Response JSON

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
                    error_msg = error_data.get("error", error_msg)
                except json.JSONDecodeError:
                    pass
                _logger.warning(
                    "Focalboard API error: %s %s -> %s: %s",
                    method,
                    endpoint,
                    response.status_code,
                    error_msg,
                )
                raise UserError(f"Focalboard API error: {error_msg}")

            if response.text:
                return response.json()
            return {}

        except requests.RequestException as e:
            _logger.error("Focalboard request failed: %s", e)
            raise UserError(f"Focalboard connection error: {e}")

    # System endpoints

    def ping(self):
        """Check if Focalboard is reachable."""
        try:
            # Try v2 ping endpoint
            self._request("GET", "/ping")
            return True
        except UserError:
            # Fallback: try base URL
            try:
                response = requests.get(
                    f"{self.base_url}/api/v2/ping", timeout=DEFAULT_TIMEOUT
                )
                return response.status_code < 400
            except requests.RequestException:
                return False

    # Board endpoints

    def get_boards(self, workspace_id=None):
        """Get all boards in a workspace."""
        if workspace_id:
            return self._request("GET", f"/teams/{workspace_id}/boards")
        return self._request("GET", "/boards")

    def get_board(self, board_id):
        """Get a specific board."""
        return self._request("GET", f"/boards/{board_id}")

    def create_board(self, data):
        """Create a new board."""
        return self._request("POST", "/boards", data=data)

    # Card endpoints

    def get_cards(self, board_id):
        """Get all cards in a board."""
        return self._request(
            "GET", f"/boards/{board_id}/blocks", params={"type": "card"}
        )

    def get_card(self, card_id):
        """Get a specific card."""
        return self._request("GET", f"/blocks/{card_id}")

    def create_card(self, board_id, data):
        """
        Create a new card on a board.

        Args:
            board_id: Board ID
            data: Card data (title, icon, fields, etc.)

        Returns:
            dict: Created card data
        """
        payload = {
            "boardId": board_id,
            "type": "card",
            "title": data.get("title", ""),
            "fields": data.get("fields", {}),
        }
        if data.get("icon"):
            payload["fields"]["icon"] = data["icon"]

        return self._request("POST", "/blocks", data=[payload])

    def update_card(self, card_id, data):
        """Update a card."""
        return self._request("PATCH", f"/blocks/{card_id}", data=data)

    def delete_card(self, card_id):
        """Delete a card."""
        return self._request("DELETE", f"/blocks/{card_id}")

    # View endpoints

    def get_views(self, board_id):
        """Get all views for a board."""
        return self._request(
            "GET", f"/boards/{board_id}/blocks", params={"type": "view"}
        )
