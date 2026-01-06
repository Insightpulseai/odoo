# -*- coding: utf-8 -*-
"""
n8n API Client

This module provides a client for the n8n REST API.
"""
import json
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class N8nClient:
    """n8n REST API client."""

    def __init__(self, connector):
        """
        Initialize the client with a connector record.

        Args:
            connector: ipai.integration.connector record
        """
        self.connector = connector
        self.base_url = connector.base_url.rstrip("/")
        self.webhook_base_url = (
            connector.n8n_webhook_url or connector.base_url
        ).rstrip("/")
        self._api_key = None

    @property
    def api_url(self):
        """Get the full API URL."""
        return f"{self.base_url}/api/v1"

    @property
    def api_key(self):
        """Get the API key."""
        if self._api_key is None:
            ICP = self.connector.env["ir.config_parameter"].sudo()
            self._api_key = ICP.get_param(
                f"ipai_n8n.api_key_{self.connector.id}",
                default=""
            )
        return self._api_key

    def _headers(self):
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key
        return headers

    def _request(self, method, endpoint, data=None, params=None, use_webhook=False):
        """
        Make an API request.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body (dict)
            params: Query parameters (dict)
            use_webhook: If True, use webhook base URL

        Returns:
            dict or list: Response JSON

        Raises:
            UserError: On API errors
        """
        base = self.webhook_base_url if use_webhook else self.api_url
        url = f"{base}{endpoint}"

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
                    "n8n API error: %s %s -> %s: %s",
                    method, endpoint, response.status_code, error_msg
                )
                raise UserError(f"n8n API error: {error_msg}")

            if response.text:
                return response.json()
            return {}

        except requests.RequestException as e:
            _logger.error("n8n request failed: %s", e)
            raise UserError(f"n8n connection error: {e}")

    # Health endpoints

    def health_check(self):
        """Check if n8n is reachable."""
        try:
            response = requests.get(
                f"{self.base_url}/healthz",
                timeout=DEFAULT_TIMEOUT
            )
            return response.status_code == 200
        except requests.RequestException:
            # Try alternative health endpoint
            try:
                response = requests.get(
                    self.base_url,
                    timeout=DEFAULT_TIMEOUT
                )
                return response.status_code < 400
            except requests.RequestException:
                return False

    # Workflow endpoints

    def get_workflows(self, active_only=False):
        """Get all workflows."""
        params = {}
        if active_only:
            params["active"] = "true"
        result = self._request("GET", "/workflows", params=params)
        return result.get("data", []) if isinstance(result, dict) else result

    def get_workflow(self, workflow_id):
        """Get a specific workflow."""
        return self._request("GET", f"/workflows/{workflow_id}")

    def activate_workflow(self, workflow_id):
        """Activate a workflow."""
        return self._request("POST", f"/workflows/{workflow_id}/activate")

    def deactivate_workflow(self, workflow_id):
        """Deactivate a workflow."""
        return self._request("POST", f"/workflows/{workflow_id}/deactivate")

    # Execution endpoints

    def get_executions(self, workflow_id=None, limit=20):
        """Get workflow executions."""
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id
        result = self._request("GET", "/executions", params=params)
        return result.get("data", []) if isinstance(result, dict) else result

    def get_execution(self, execution_id):
        """Get a specific execution."""
        return self._request("GET", f"/executions/{execution_id}")

    # Webhook endpoints

    def trigger_webhook(self, path, payload):
        """
        Trigger an n8n webhook.

        Args:
            path: Webhook path (e.g., /webhook/abc123)
            payload: Data to send

        Returns:
            dict: Webhook response
        """
        if not path.startswith("/"):
            path = f"/webhook/{path}"

        try:
            response = requests.post(
                f"{self.webhook_base_url}{path}",
                json=payload,
                timeout=DEFAULT_TIMEOUT,
            )

            # Log the execution
            self.connector.env["ipai.integration.audit"].sudo().log(
                self.connector.id,
                "webhook_trigger",
                f"Triggered webhook: {path}",
                request_method="POST",
                request_url=f"{self.webhook_base_url}{path}",
                response_code=response.status_code,
            )

            if response.status_code >= 400:
                _logger.warning(
                    "n8n webhook error: %s -> %s",
                    path, response.status_code
                )
                return None

            if response.text:
                return response.json()
            return {"status": "ok"}

        except requests.RequestException as e:
            _logger.error("n8n webhook failed: %s", e)
            return None

    # Credential endpoints (for reference only - don't store actual creds)

    def get_credentials(self):
        """Get credential metadata (not actual values)."""
        result = self._request("GET", "/credentials")
        return result.get("data", []) if isinstance(result, dict) else result
