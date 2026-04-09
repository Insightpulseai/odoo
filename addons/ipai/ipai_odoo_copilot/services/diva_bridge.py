# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import json
import logging

import requests

from odoo import api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DIVA_TIMEOUT_SECONDS = 30


class DivaBridge(models.AbstractModel):
    """Bridge to Diva Goals backend (Foundry Agent Service).

    Sends normalized Odoo context, receives advisory responses.
    Never executes business logic — that stays in the agent layer.
    """

    _name = 'ipai.copilot.diva.bridge'
    _description = 'Diva Goals Backend Bridge'

    def _get_endpoint(self):
        """Resolve Diva backend endpoint from system parameters."""
        endpoint = self.env['ir.config_parameter'].sudo().get_param(
            'ipai_copilot.diva_endpoint', default=''
        )
        if not endpoint:
            _logger.warning("ipai_copilot.diva_endpoint not configured")
        return endpoint

    def _get_api_key(self):
        """Resolve API key from system parameters (Key Vault backed)."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'ipai_copilot.diva_api_key', default=''
        )

    @api.model
    def send_advisory_request(self, workflow_id, context_payload):
        """Send an advisory request to Diva Goals backend.

        Args:
            workflow_id: Diva workflow identifier (e.g. 'goal-status-synthesis')
            context_payload: dict from OdooContextBuilder

        Returns:
            dict with advisory response or error
        """
        endpoint = self._get_endpoint()
        if not endpoint:
            return {'status': 'error', 'message': 'Diva endpoint not configured'}

        api_key = self._get_api_key()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }
        payload = {
            'workflow_id': workflow_id,
            'context': context_payload,
            'source': 'odoo_copilot',
        }

        try:
            resp = requests.post(
                f'{endpoint}/api/v1/advisory',
                json=payload,
                headers=headers,
                timeout=DIVA_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.Timeout:
            _logger.error("Diva backend timeout for workflow %s", workflow_id)
            return {'status': 'error', 'message': 'Diva backend timeout'}
        except requests.RequestException as e:
            _logger.error("Diva backend error: %s", e)
            return {'status': 'error', 'message': str(e)}

    @api.model
    def query_goal_status(self, goal_id=None):
        """Query goal status from Diva Goals backend (read-only)."""
        endpoint = self._get_endpoint()
        if not endpoint:
            return {'status': 'error', 'message': 'Diva endpoint not configured'}

        api_key = self._get_api_key()
        headers = {'Authorization': f'Bearer {api_key}'}
        params = {}
        if goal_id:
            params['goal_id'] = goal_id

        try:
            resp = requests.get(
                f'{endpoint}/api/v1/goals/status',
                params=params,
                headers=headers,
                timeout=DIVA_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            _logger.error("Diva goal status query error: %s", e)
            return {'status': 'error', 'message': str(e)}
