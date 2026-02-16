# -*- coding: utf-8 -*-
"""
Native REST API Controllers
============================

Interim solution for REST endpoints while waiting for OCA base_rest 19.0 migration.

TODO: Migrate to base_rest when available
- Replace with base_rest.RestController inheritance
- Use base_rest decorators and response helpers
- Preserve API contract for backward compatibility

Authentication:
- Session-based: Use Odoo session cookies (web client)
- API Key: Custom header X-API-Key (external integrations)

Error Handling:
- Returns JSON with error details
- HTTP status codes: 200 (success), 400 (bad request), 401 (unauthorized), 500 (server error)
"""

import json
import logging
from functools import wraps

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)


def validate_api_key(func):
    """
    Decorator to validate API key from X-API-Key header.

    TODO: Implement proper API key model and validation
    For now, accepts any non-empty key for demonstration.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.httprequest.headers.get('X-API-Key')
        if not api_key:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 401,
                    'message': 'Unauthorized: Missing X-API-Key header'
                }
            }

        # TODO: Validate API key against database
        # For now, just check it's not empty
        if not api_key.strip():
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 401,
                    'message': 'Unauthorized: Invalid API key'
                }
            }

        return func(*args, **kwargs)
    return wrapper


class IPAIRESTController(http.Controller):
    """
    Native REST API controller for external integrations.

    Endpoints:
    - /api/v1/health - Health check
    - /api/v1/echo - Echo test endpoint

    TODO: Add actual business endpoints as needed
    """

    @http.route('/api/v1/health', type='json', auth='none', methods=['GET', 'POST'], csrf=False)
    def health_check(self, **kwargs):
        """
        Health check endpoint for monitoring.

        Returns:
            dict: Status and version info
        """
        try:
            return {
                'status': 'ok',
                'service': 'ipai-rest-controllers',
                'version': '19.0.1.0.0',
                'odoo_version': request.env['ir.module.module'].sudo().search([
                    ('name', '=', 'base')
                ], limit=1).installed_version or 'unknown'
            }
        except Exception as e:
            _logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/v1/echo', type='json', auth='user', methods=['POST'], csrf=False)
    @validate_api_key
    def echo(self, **kwargs):
        """
        Echo endpoint for testing JSON-RPC requests.

        Params:
            message (str): Message to echo back

        Returns:
            dict: Echoed message with metadata
        """
        try:
            message = kwargs.get('message', '')

            if not message:
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 400,
                        'message': 'Bad Request: Missing message parameter'
                    }
                }

            return {
                'jsonrpc': '2.0',
                'result': {
                    'status': 'success',
                    'echo': message,
                    'user': request.env.user.name,
                    'timestamp': http.request.httprequest.headers.get('Date')
                }
            }
        except ValidationError as e:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 400,
                    'message': f'Validation Error: {str(e)}'
                }
            }
        except AccessError as e:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 403,
                    'message': f'Access Denied: {str(e)}'
                }
            }
        except Exception as e:
            _logger.error(f"Echo endpoint error: {e}", exc_info=True)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 500,
                    'message': f'Internal Server Error: {str(e)}'
                }
            }


class IPAIRESTExampleController(http.Controller):
    """
    Example REST endpoints demonstrating patterns for business logic.

    TODO: Replace with actual business endpoints
    """

    @http.route('/api/v1/partners/search', type='json', auth='user', methods=['POST'], csrf=False)
    @validate_api_key
    def search_partners(self, **kwargs):
        """
        Example: Search partners by name.

        Params:
            name (str): Partner name to search
            limit (int): Max results (default: 10)

        Returns:
            dict: List of matching partners
        """
        try:
            name = kwargs.get('name', '')
            limit = kwargs.get('limit', 10)

            if not name:
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 400,
                        'message': 'Bad Request: Missing name parameter'
                    }
                }

            partners = request.env['res.partner'].search([
                ('name', 'ilike', name)
            ], limit=limit)

            return {
                'jsonrpc': '2.0',
                'result': {
                    'status': 'success',
                    'count': len(partners),
                    'partners': [{
                        'id': p.id,
                        'name': p.name,
                        'email': p.email or '',
                        'phone': p.phone or ''
                    } for p in partners]
                }
            }
        except Exception as e:
            _logger.error(f"Partner search error: {e}", exc_info=True)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 500,
                    'message': f'Internal Server Error: {str(e)}'
                }
            }
