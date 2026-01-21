# -*- coding: utf-8 -*-
"""
IPAI IoT API Controllers

REST API endpoints for IoT device integration.
"""

import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IpaiIotApiController(http.Controller):
    """REST API for IoT devices."""

    @http.route("/ipai/iot/devices", type="json", auth="user")
    def get_devices(self, device_type=None, gateway_id=None, **kwargs):
        """Get list of IoT devices."""
        domain = [("active", "=", True)]

        if device_type:
            domain.append(("device_type", "=", device_type))
        if gateway_id:
            domain.append(("gateway_id", "=", int(gateway_id)))

        devices = request.env["ipai.iot.device"].search(domain)

        return [{
            "id": d.id,
            "name": d.name,
            "identifier": d.identifier,
            "device_type": d.device_type,
            "connection_type": d.connection_type,
            "state": d.state,
            "gateway_id": d.gateway_id.id if d.gateway_id else None,
            "gateway_name": d.gateway_id.name if d.gateway_id else None,
        } for d in devices]

    @http.route("/ipai/iot/device/<int:device_id>/print", type="json", auth="user")
    def print_to_device(self, device_id, content, **kwargs):
        """Send print job to device."""
        device = request.env["ipai.iot.device"].browse(device_id)

        if not device.exists():
            return {"success": False, "error": "Device not found"}

        if device.device_type != "printer":
            return {"success": False, "error": "Not a printer device"}

        try:
            device.print_receipt(content)
            return {"success": True, "message": "Print job sent"}
        except Exception as e:
            _logger.exception("Print failed for device %s", device_id)
            return {"success": False, "error": str(e)}

    @http.route("/ipai/iot/gateways", type="json", auth="user")
    def get_gateways(self, **kwargs):
        """Get list of IoT gateways."""
        gateways = request.env["ipai.iot.gateway"].search([("active", "=", True)])

        return [{
            "id": g.id,
            "name": g.name,
            "gateway_type": g.gateway_type,
            "state": g.state,
            "device_count": g.device_count,
        } for g in gateways]

    @http.route("/ipai/iot/gateway/<int:gateway_id>/discover", type="json", auth="user")
    def discover_devices(self, gateway_id, **kwargs):
        """Trigger device discovery on gateway."""
        gateway = request.env["ipai.iot.gateway"].browse(gateway_id)

        if not gateway.exists():
            return {"success": False, "error": "Gateway not found"}

        try:
            gateway.action_discover_devices()
            return {
                "success": True,
                "message": f"Discovery complete, found {gateway.device_count} devices",
            }
        except Exception as e:
            _logger.exception("Discovery failed for gateway %s", gateway_id)
            return {"success": False, "error": str(e)}

    @http.route("/ipai/iot/status", type="http", auth="none", csrf=False)
    def health_check(self, **kwargs):
        """Health check endpoint for IoT service."""
        return json.dumps({
            "status": "ok",
            "service": "ipai_iot_bridge",
            "version": "18.0.1.0.0",
        })
