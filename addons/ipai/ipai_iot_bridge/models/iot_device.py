# -*- coding: utf-8 -*-
"""
IoT Device - Direct Device Communication

Provides device management without Enterprise IoT box.
"""
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiIotDevice(models.Model):
    """IoT Device Registry."""

    _name = "ipai.iot.device"
    _description = "IoT Device"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Device Name",
        required=True,
        tracking=True,
    )
    device_code = fields.Char(
        string="Device Code",
        required=True,
        copy=False,
        index=True,
    )
    device_type = fields.Selection(
        [
            ("sensor", "Sensor"),
            ("actuator", "Actuator"),
            ("gateway", "Gateway"),
            ("controller", "Controller"),
            ("display", "Display"),
            ("printer", "Printer"),
            ("scanner", "Scanner"),
            ("other", "Other"),
        ],
        string="Device Type",
        required=True,
        default="sensor",
        tracking=True,
    )
    protocol = fields.Selection(
        [
            ("mqtt", "MQTT"),
            ("http", "HTTP/REST"),
            ("modbus", "Modbus"),
            ("opcua", "OPC UA"),
            ("websocket", "WebSocket"),
            ("serial", "Serial"),
        ],
        string="Protocol",
        required=True,
        default="http",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("error", "Error"),
            ("maintenance", "Maintenance"),
            ("archived", "Archived"),
        ],
        string="State",
        default="draft",
        tracking=True,
    )

    # Connection Configuration
    host = fields.Char(
        string="Host/IP",
        help="Device IP address or hostname",
    )
    port = fields.Integer(
        string="Port",
        default=80,
    )
    endpoint = fields.Char(
        string="API Endpoint",
        help="REST API endpoint path",
    )
    api_key = fields.Char(
        string="API Key",
    )
    username = fields.Char(
        string="Username",
    )
    password = fields.Char(
        string="Password",
    )

    # MQTT Configuration
    mqtt_topic_subscribe = fields.Char(
        string="Subscribe Topic",
        help="MQTT topic to subscribe for incoming data",
    )
    mqtt_topic_publish = fields.Char(
        string="Publish Topic",
        help="MQTT topic to publish commands",
    )
    mqtt_qos = fields.Selection(
        [
            ("0", "At most once (0)"),
            ("1", "At least once (1)"),
            ("2", "Exactly once (2)"),
        ],
        string="QoS Level",
        default="1",
    )

    # Status
    last_seen = fields.Datetime(
        string="Last Seen",
        readonly=True,
    )
    last_error = fields.Text(
        string="Last Error",
        readonly=True,
    )
    reading_count = fields.Integer(
        string="Reading Count",
        compute="_compute_reading_count",
    )

    # Location
    location = fields.Char(
        string="Location",
    )
    latitude = fields.Float(
        string="Latitude",
        digits=(10, 7),
    )
    longitude = fields.Float(
        string="Longitude",
        digits=(10, 7),
    )

    # Metadata
    manufacturer = fields.Char(
        string="Manufacturer",
    )
    model = fields.Char(
        string="Model",
    )
    serial_number = fields.Char(
        string="Serial Number",
    )
    firmware_version = fields.Char(
        string="Firmware Version",
    )

    _sql_constraints = [
        (
            "device_code_unique",
            "UNIQUE(device_code)",
            "Device code must be unique.",
        ),
    ]

    def _compute_reading_count(self):
        """Compute number of readings for this device."""
        Reading = self.env["ipai.iot.reading"]
        for device in self:
            device.reading_count = Reading.search_count([("device_id", "=", device.id)])

    def action_activate(self):
        """Activate device."""
        self.write({"state": "active"})

    def action_deactivate(self):
        """Set device to draft."""
        self.write({"state": "draft"})

    def action_set_maintenance(self):
        """Set device to maintenance mode."""
        self.write({"state": "maintenance"})

    def action_test_connection(self):
        """Test device connection."""
        self.ensure_one()
        try:
            if self.protocol == "http":
                return self._test_http_connection()
            elif self.protocol == "mqtt":
                return self._test_mqtt_connection()
            else:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "Connection Test",
                        "message": f"Test not implemented for {self.protocol}",
                        "type": "warning",
                    },
                }
        except Exception as e:
            self.write({"state": "error", "last_error": str(e)})
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Connection Failed",
                    "message": str(e),
                    "type": "danger",
                },
            }

    def _test_http_connection(self):
        """Test HTTP/REST connection."""
        import requests

        url = f"http://{self.host}:{self.port}"
        if self.endpoint:
            url = f"{url}/{self.endpoint.lstrip('/')}"

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            self.write({"state": "active", "last_seen": fields.Datetime.now()})
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Connection Successful",
                    "message": "Device is reachable",
                    "type": "success",
                },
            }
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    def _test_mqtt_connection(self):
        """Test MQTT connection (placeholder)."""
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "MQTT Test",
                "message": "MQTT connection test requires broker configuration",
                "type": "info",
            },
        }

    def action_view_readings(self):
        """View readings for this device."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Readings - {self.name}",
            "res_model": "ipai.iot.reading",
            "view_mode": "tree,form",
            "domain": [("device_id", "=", self.id)],
            "context": {"default_device_id": self.id},
        }


class IpaiIotDeviceType(models.Model):
    """Device type configuration."""

    _name = "ipai.iot.device.type"
    _description = "IoT Device Type"

    name = fields.Char(
        string="Type Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
    default_protocol = fields.Selection(
        [
            ("mqtt", "MQTT"),
            ("http", "HTTP/REST"),
            ("modbus", "Modbus"),
            ("opcua", "OPC UA"),
            ("websocket", "WebSocket"),
            ("serial", "Serial"),
        ],
        string="Default Protocol",
        default="http",
    )
