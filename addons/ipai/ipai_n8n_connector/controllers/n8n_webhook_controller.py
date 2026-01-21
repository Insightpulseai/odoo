# -*- coding: utf-8 -*-
"""
Controller for receiving webhooks from n8n.

n8n can call back to Odoo after workflow execution or as part of
a workflow that needs to update Odoo data.
"""
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class N8nWebhookController(http.Controller):
    """Controller for n8n webhook callbacks."""

    @http.route(
        "/integrations/n8n/callback",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def n8n_callback(self, **kwargs):
        """
        Generic callback endpoint for n8n workflows.

        Expected payload:
        {
            "workflow_id": "...",
            "execution_id": "...",
            "status": "success|error",
            "data": {...}
        }
        """
        payload = request.jsonrequest or {}

        # Log the callback
        request.env["ipai.integration.audit"].sudo().log(
            None,  # No specific connector
            "n8n_callback",
            f"Callback from n8n workflow: {payload.get('workflow_id')}",
            request_method="POST",
            request_payload=json.dumps(payload),
        )

        # Find the workflow
        n8n_workflow_id = payload.get("workflow_id")
        if n8n_workflow_id:
            workflow = (
                request.env["ipai.n8n.workflow"]
                .sudo()
                .search([("n8n_workflow_id", "=", str(n8n_workflow_id))], limit=1)
            )

            if workflow:
                # Log execution
                request.env["ipai.n8n.execution"].sudo().create(
                    {
                        "workflow_id": workflow.id,
                        "n8n_execution_id": payload.get("execution_id"),
                        "trigger_source": "webhook",
                        "status": payload.get("status", "success"),
                        "output_data": json.dumps(payload.get("data", {})),
                        "started_at": request.env.cr.now(),
                        "finished_at": request.env.cr.now(),
                    }
                )

        return {"status": "ok"}

    @http.route(
        "/integrations/n8n/trigger/<string:action>",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def n8n_trigger_action(self, action, **kwargs):
        """
        Endpoint for n8n to trigger specific Odoo actions.

        Supported actions:
        - create_record: Create a new record
        - update_record: Update an existing record
        - run_method: Run a method on a model
        """
        payload = request.jsonrequest or {}

        # Validate signature if configured
        signature = request.httprequest.headers.get("X-N8N-Signature")
        if signature:
            # Implement signature validation here
            pass

        result = {"status": "error", "message": "Unknown action"}

        try:
            if action == "create_record":
                result = self._handle_create_record(payload)
            elif action == "update_record":
                result = self._handle_update_record(payload)
            elif action == "run_method":
                result = self._handle_run_method(payload)
            else:
                result = {"status": "error", "message": f"Unknown action: {action}"}
        except Exception as e:
            _logger.exception("n8n trigger action failed")
            result = {"status": "error", "message": str(e)}

        return result

    def _handle_create_record(self, payload):
        """Handle record creation."""
        model = payload.get("model")
        values = payload.get("values", {})

        if not model or not values:
            return {"status": "error", "message": "Missing model or values"}

        try:
            Model = request.env[model].sudo()
            record = Model.create(values)
            return {
                "status": "success",
                "record_id": record.id,
                "record_name": (
                    record.display_name
                    if hasattr(record, "display_name")
                    else str(record.id)
                ),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_update_record(self, payload):
        """Handle record update."""
        model = payload.get("model")
        record_id = payload.get("record_id")
        values = payload.get("values", {})

        if not model or not record_id or not values:
            return {"status": "error", "message": "Missing model, record_id, or values"}

        try:
            Model = request.env[model].sudo()
            record = Model.browse(int(record_id))
            if not record.exists():
                return {"status": "error", "message": "Record not found"}
            record.write(values)
            return {"status": "success", "record_id": record.id}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_run_method(self, payload):
        """Handle method execution."""
        model = payload.get("model")
        method = payload.get("method")
        args = payload.get("args", [])
        kwargs = payload.get("kwargs", {})
        record_id = payload.get("record_id")

        if not model or not method:
            return {"status": "error", "message": "Missing model or method"}

        # Whitelist of allowed methods for security
        allowed_methods = [
            "action_",  # Prefix for action methods
            "button_",  # Prefix for button methods
            "_handle_",  # Prefix for handler methods
        ]

        is_allowed = any(method.startswith(prefix) for prefix in allowed_methods)
        if not is_allowed:
            return {"status": "error", "message": f"Method not allowed: {method}"}

        try:
            Model = request.env[model].sudo()
            if record_id:
                target = Model.browse(int(record_id))
            else:
                target = Model

            if not hasattr(target, method):
                return {"status": "error", "message": f"Method not found: {method}"}

            result = getattr(target, method)(*args, **kwargs)
            return {"status": "success", "result": str(result) if result else None}
        except Exception as e:
            return {"status": "error", "message": str(e)}
