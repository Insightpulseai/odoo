# -*- coding: utf-8 -*-
"""
IPAI IoT Gateway

CE-safe replacement for EE iot.box model.
This model does NOT inherit from any EE models.
"""

import logging
import requests
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiIotGateway(models.Model):
    """IoT Gateway (replaces EE iot.box)."""

    _name = "ipai.iot.gateway"
    _description = "IPAI IoT Gateway"
    _order = "sequence, name"

    name = fields.Char(required=True, string="Gateway Name")
    sequence = fields.Integer(default=10)

    gateway_type = fields.Selection(
        [
            ("self_hosted", "Self-Hosted Gateway"),
            ("cups", "CUPS Print Server"),
            ("printnode", "PrintNode Cloud"),
            ("escpos_network", "ESC/POS Network Direct"),
        ],
        required=True,
        default="self_hosted",
        string="Gateway Type",
    )

    # Network Configuration
    ip_address = fields.Char(string="IP Address / Hostname")
    port = fields.Integer(string="Port", default=8080)
    use_ssl = fields.Boolean(string="Use SSL/TLS", default=False)

    # Authentication
    api_key = fields.Char(string="API Key")
    username = fields.Char(string="Username")
    password = fields.Char(string="Password")

    # CUPS specific
    cups_server = fields.Char(
        string="CUPS Server",
        help="CUPS server address (e.g., localhost:631)",
    )

    # PrintNode specific
    printnode_api_key = fields.Char(string="PrintNode API Key")

    # State
    state = fields.Selection(
        [
            ("draft", "Not Connected"),
            ("connected", "Connected"),
            ("error", "Error"),
        ],
        default="draft",
        string="Status",
        compute="_compute_state",
        store=True,
    )
    last_seen = fields.Datetime(string="Last Seen")
    error_message = fields.Text(string="Error Message")

    # Devices
    device_ids = fields.One2many(
        "ipai.iot.device",
        "gateway_id",
        string="Devices",
    )
    device_count = fields.Integer(
        string="Device Count",
        compute="_compute_device_count",
    )

    active = fields.Boolean(default=True)

    @api.depends("device_ids")
    def _compute_device_count(self):
        for rec in self:
            rec.device_count = len(rec.device_ids)

    @api.depends("last_seen", "error_message")
    def _compute_state(self):
        from datetime import timedelta

        for rec in self:
            if rec.error_message:
                rec.state = "error"
            elif rec.last_seen and rec.last_seen > fields.Datetime.now() - timedelta(minutes=5):
                rec.state = "connected"
            else:
                rec.state = "draft"

    def _get_base_url(self):
        """Get gateway base URL."""
        self.ensure_one()
        protocol = "https" if self.use_ssl else "http"
        return f"{protocol}://{self.ip_address}:{self.port}"

    def action_test_connection(self):
        """Test connection to gateway."""
        self.ensure_one()

        try:
            if self.gateway_type == "self_hosted":
                url = f"{self._get_base_url()}/status"
                response = requests.get(url, timeout=5)
                response.raise_for_status()

            elif self.gateway_type == "cups":
                # Test CUPS connection
                import subprocess

                result = subprocess.run(
                    ["lpstat", "-h", self.cups_server or "localhost", "-v"],
                    capture_output=True,
                    timeout=5,
                )
                if result.returncode != 0:
                    raise Exception(result.stderr.decode())

            elif self.gateway_type == "printnode":
                response = requests.get(
                    "https://api.printnode.com/whoami",
                    auth=(self.printnode_api_key, ""),
                    timeout=5,
                )
                response.raise_for_status()

            elif self.gateway_type == "escpos_network":
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((self.ip_address, self.port or 9100))
                sock.close()

            self.write({
                "last_seen": fields.Datetime.now(),
                "error_message": False,
            })

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Connection Test",
                    "message": f"Successfully connected to {self.name}",
                    "type": "success",
                },
            }

        except Exception as e:
            self.write({"error_message": str(e)})
            raise UserError(f"Connection failed: {e}")

    def action_discover_devices(self):
        """Discover devices on this gateway."""
        self.ensure_one()

        if self.gateway_type == "cups":
            self._discover_cups_printers()
        elif self.gateway_type == "printnode":
            self._discover_printnode_printers()
        elif self.gateway_type == "self_hosted":
            self._discover_gateway_devices()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Discovery Complete",
                "message": f"Found {self.device_count} devices",
                "type": "success",
            },
        }

    def _discover_cups_printers(self):
        """Discover printers from CUPS server."""
        import subprocess

        result = subprocess.run(
            ["lpstat", "-h", self.cups_server or "localhost", "-v"],
            capture_output=True,
            timeout=10,
        )

        if result.returncode != 0:
            raise UserError(f"CUPS error: {result.stderr.decode()}")

        Device = self.env["ipai.iot.device"]

        for line in result.stdout.decode().split("\n"):
            if not line.strip():
                continue

            # Parse: device for printer_name: uri
            parts = line.split(":")
            if len(parts) >= 2:
                printer_name = parts[0].replace("device for ", "").strip()

                existing = Device.search([
                    ("gateway_id", "=", self.id),
                    ("identifier", "=", printer_name),
                ], limit=1)

                if not existing:
                    Device.create({
                        "name": printer_name,
                        "identifier": printer_name,
                        "gateway_id": self.id,
                        "device_type": "printer",
                        "connection_type": "cups",
                        "cups_printer_name": printer_name,
                    })

    def _discover_printnode_printers(self):
        """Discover printers from PrintNode."""
        response = requests.get(
            "https://api.printnode.com/printers",
            auth=(self.printnode_api_key, ""),
            timeout=10,
        )
        response.raise_for_status()

        Device = self.env["ipai.iot.device"]

        for printer in response.json():
            existing = Device.search([
                ("gateway_id", "=", self.id),
                ("identifier", "=", str(printer["id"])),
            ], limit=1)

            if not existing:
                Device.create({
                    "name": printer["name"],
                    "identifier": str(printer["id"]),
                    "gateway_id": self.id,
                    "device_type": "printer",
                    "connection_type": "printnode",
                    "printnode_printer_id": printer["id"],
                })

    def _discover_gateway_devices(self):
        """Discover devices from self-hosted gateway."""
        url = f"{self._get_base_url()}/devices"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        Device = self.env["ipai.iot.device"]

        for device in response.json().get("devices", []):
            existing = Device.search([
                ("gateway_id", "=", self.id),
                ("identifier", "=", device.get("id")),
            ], limit=1)

            if not existing:
                Device.create({
                    "name": device.get("name", "Unknown Device"),
                    "identifier": device.get("id"),
                    "gateway_id": self.id,
                    "device_type": device.get("type", "other"),
                    "connection_type": device.get("connection", "network"),
                    "ip_address": device.get("ip"),
                })
