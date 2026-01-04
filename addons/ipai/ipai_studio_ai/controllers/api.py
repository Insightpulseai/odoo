# -*- coding: utf-8 -*-
"""
IPAI Studio AI - JSON API Controller

Provides HTTP endpoints for external clients (ChatGPT Apps, MCP servers, etc.)
to interact with Studio AI functionality.

Endpoints:
- /ipai_studio_ai/api/process_command - Process NLP command
- /ipai_studio_ai/api/analyze - Analyze command (dry run)
- /ipai_studio_ai/api/create_field - Create custom field
- /ipai_studio_ai/api/query - Execute data query
- /ipai_studio_ai/api/module_info - Get module information

Authentication:
- Session-based (auth="user") for logged-in users
- Token-based (auth="public" + Bearer token) for API clients

Author: InsightPulse AI
License: AGPL-3
"""

import json
import logging

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)


def _get_api_token():
    """Get configured API token from system parameters."""
    icp = request.env["ir.config_parameter"].sudo()
    return (icp.get_param("ipai_studio_ai.api_token") or "").strip()


def _require_token_if_configured():
    """
    Check Bearer token if API token is configured.
    Raises AccessError if token is missing or invalid.
    """
    token = _get_api_token()
    if not token:
        return  # No token configured, allow access

    auth_header = (request.httprequest.headers.get("Authorization") or "").strip()
    if not auth_header.startswith("Bearer "):
        raise AccessError("Missing Bearer token in Authorization header")

    provided_token = auth_header.split(" ", 1)[1].strip()
    if provided_token != token:
        raise AccessError("Invalid API token")


def _json_response(data, status=200):
    """Create JSON response with proper content type."""
    return {"ok": True, "data": data}


def _json_error(message, code="error"):
    """Create error response."""
    return {"ok": False, "error": {"code": code, "message": str(message)}}


class IpaiStudioAiApiController(http.Controller):
    """JSON API controller for Studio AI."""

    # =========================================================================
    # SESSION-AUTHENTICATED ENDPOINTS (auth="user")
    # Requires login via /web/session/authenticate
    # =========================================================================

    @http.route(
        "/ipai_studio_ai/api/process_command",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False
    )
    def process_command(self, command, context=None):
        """
        Process a natural language command.

        Args:
            command (str): Natural language command
            context (dict): Optional context (model, view, etc.)

        Returns:
            dict: Analysis result with type, confidence, ready status
        """
        try:
            if not command:
                return _json_error("Command is required", "validation_error")

            service = request.env["ipai.studio.ai.service"]
            result = service.process_command(command, context or {})

            return _json_response(result)

        except Exception as e:
            _logger.exception("Error processing command")
            return _json_error(str(e))

    @http.route(
        "/ipai_studio_ai/api/analyze",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False
    )
    def analyze_command(self, command):
        """
        Analyze a command without executing (dry run).

        Args:
            command (str): Command to analyze

        Returns:
            dict: Analysis result
        """
        try:
            if not command:
                return _json_error("Command is required", "validation_error")

            service = request.env["ipai.studio.ai.service"]
            result = service.process_command(command, {"dry_run": True})

            # Add analysis-only flag
            result["executed"] = False

            return _json_response(result)

        except Exception as e:
            _logger.exception("Error analyzing command")
            return _json_error(str(e))

    @http.route(
        "/ipai_studio_ai/api/create_field",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False
    )
    def create_field(self, model, field_name, field_type, label, required=False):
        """
        Create a custom field on a model.

        Args:
            model (str): Target model (e.g., 'res.partner')
            field_name (str): Technical name (e.g., 'x_phone_2')
            field_type (str): Odoo field type
            label (str): Human-readable label
            required (bool): Is field required

        Returns:
            dict: Created field info
        """
        try:
            # Validate inputs
            if not all([model, field_name, field_type, label]):
                return _json_error("model, field_name, field_type, and label are required", "validation_error")

            if not field_name.startswith("x_"):
                field_name = f"x_{field_name}"

            # Check model exists
            model_rec = request.env["ir.model"].sudo().search([("model", "=", model)], limit=1)
            if not model_rec:
                return _json_error(f"Model '{model}' not found", "not_found")

            # Check field doesn't exist
            existing = request.env["ir.model.fields"].sudo().search([
                ("model", "=", model),
                ("name", "=", field_name)
            ], limit=1)
            if existing:
                return _json_error(f"Field '{field_name}' already exists on {model}", "exists")

            # Create field
            field_vals = {
                "name": field_name,
                "field_description": label,
                "model_id": model_rec.id,
                "ttype": field_type,
                "required": required,
                "state": "manual",
            }

            new_field = request.env["ir.model.fields"].sudo().create(field_vals)

            return _json_response({
                "id": new_field.id,
                "name": new_field.name,
                "model": model,
                "type": field_type,
                "label": label,
                "required": required,
            })

        except Exception as e:
            _logger.exception("Error creating field")
            return _json_error(str(e))

    @http.route(
        "/ipai_studio_ai/api/query",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False
    )
    def execute_query(self, query_type, model, domain=None, limit=10, fields=None):
        """
        Execute a data query.

        Args:
            query_type (str): 'list' or 'count'
            model (str): Model to query
            domain (list): Search domain
            limit (int): Result limit
            fields (list): Fields to return (for list)

        Returns:
            dict: Query results
        """
        try:
            if not model:
                return _json_error("Model is required", "validation_error")

            if model not in request.env:
                return _json_error(f"Model '{model}' not found", "not_found")

            Model = request.env[model]
            search_domain = domain or []

            if query_type == "count":
                count = Model.search_count(search_domain)
                return _json_response({"count": count, "model": model})

            else:  # list
                records = Model.search(search_domain, limit=limit)

                # Default fields
                if not fields:
                    fields = ["id", "display_name"]
                    if "name" in Model._fields:
                        fields.append("name")

                # Filter to existing fields
                valid_fields = [f for f in fields if f in Model._fields]

                results = []
                for rec in records:
                    row = {}
                    for field in valid_fields:
                        val = getattr(rec, field, None)
                        if hasattr(val, "id"):  # Many2one
                            row[field] = {"id": val.id, "name": val.display_name}
                        else:
                            row[field] = val
                    results.append(row)

                return _json_response({
                    "model": model,
                    "count": len(results),
                    "records": results,
                })

        except Exception as e:
            _logger.exception("Error executing query")
            return _json_error(str(e))

    @http.route(
        "/ipai_studio_ai/api/module_info",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False
    )
    def module_info(self, module_name):
        """
        Get module information.

        Args:
            module_name (str): Technical module name

        Returns:
            dict: Module info (name, version, state, depends)
        """
        try:
            if not module_name:
                return _json_error("module_name is required", "validation_error")

            Module = request.env["ir.module.module"].sudo()
            module = Module.search([("name", "=", module_name)], limit=1)

            if not module:
                return _json_error(f"Module '{module_name}' not found", "not_found")

            return _json_response({
                "name": module.name,
                "shortdesc": module.shortdesc,
                "version": module.installed_version or module.latest_version,
                "state": module.state,
                "author": module.author,
                "summary": module.summary,
                "depends": [d.name for d in module.dependencies_id],
            })

        except Exception as e:
            _logger.exception("Error getting module info")
            return _json_error(str(e))

    # =========================================================================
    # TOKEN-AUTHENTICATED ENDPOINTS (auth="public")
    # For external API clients with Bearer token
    # =========================================================================

    @http.route(
        "/ipai_studio_ai/api/public/process_command",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False
    )
    def public_process_command(self, command, context=None):
        """
        Public API: Process NLP command.
        Requires Bearer token if ipai_studio_ai.api_token is configured.
        """
        try:
            _require_token_if_configured()

            if not command:
                return _json_error("Command is required", "validation_error")

            # Use sudo for public access
            service = request.env["ipai.studio.ai.service"].sudo()
            result = service.process_command(command, context or {})

            return _json_response(result)

        except AccessError as e:
            return _json_error(str(e), "auth_error")
        except Exception as e:
            _logger.exception("Error in public process_command")
            return _json_error(str(e))

    @http.route(
        "/ipai_studio_ai/api/public/query",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False
    )
    def public_query(self, query_type, model, domain=None, limit=10):
        """
        Public API: Execute read-only query.
        Requires Bearer token if configured.
        """
        try:
            _require_token_if_configured()

            if not model:
                return _json_error("Model is required", "validation_error")

            # Restrict to safe models for public access
            safe_models = [
                "ir.module.module",
                "res.country",
                "res.currency",
            ]

            if model not in safe_models:
                return _json_error(f"Model '{model}' not allowed for public access", "forbidden")

            Model = request.env[model].sudo()
            search_domain = domain or []

            if query_type == "count":
                count = Model.search_count(search_domain)
                return _json_response({"count": count, "model": model})

            else:
                records = Model.search(search_domain, limit=min(limit, 100))
                results = [{"id": r.id, "display_name": r.display_name} for r in records]
                return _json_response({
                    "model": model,
                    "count": len(results),
                    "records": results,
                })

        except AccessError as e:
            return _json_error(str(e), "auth_error")
        except Exception as e:
            _logger.exception("Error in public query")
            return _json_error(str(e))

    # =========================================================================
    # HEALTH CHECK
    # =========================================================================

    @http.route(
        "/ipai_studio_ai/api/health",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False
    )
    def health(self):
        """Health check endpoint."""
        import json
        response = json.dumps({
            "status": "ok",
            "service": "ipai_studio_ai",
            "version": "18.0.1.0.0",
        })
        return request.make_response(
            response,
            headers=[("Content-Type", "application/json")]
        )
