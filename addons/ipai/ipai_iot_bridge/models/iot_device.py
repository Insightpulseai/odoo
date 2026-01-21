# -*- coding: utf-8 -*-
"""
IPAI IoT Device

CE-safe replacement for EE iot.device model.
This model does NOT inherit from any EE models.
"""

import logging
import requests
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiIotDevice(models.Model):
    """IoT Device (replaces EE iot.device)."""

    _name = "ipai.iot.device"
    _description = "IPAI IoT Device"
    _order = "sequence, name"

    name = fields.Char(required=True, string="Device Name")
    identifier = fields.Char(string="Device Identifier", index=True)
    sequence = fields.Integer(default=10)

    device_type = fields.Selection(
        [
            ("printer", "Printer"),
            ("scale", "Scale"),
            ("scanner", "Barcode Scanner"),
            ("display", "Customer Display"),
            ("payment", "Payment Terminal"),
            ("camera", "Camera"),
            ("other", "Other"),
        ],
        required=True,
        default="printer",
        string="Device Type",
    )

    connection_type = fields.Selection(
        [
            ("usb", "USB"),
            ("network", "Network/TCP"),
            ("serial", "Serial Port"),
            ("cups", "CUPS"),
            ("printnode", "PrintNode Cloud"),
            ("escpos", "ESC/POS Direct"),
        ],
        required=True,
        default="network",
        string="Connection Type",
    )

    # Gateway
    gateway_id = fields.Many2one(
        "ipai.iot.gateway",
        string="Gateway",
        ondelete="cascade",
    )

    # Network settings
    ip_address = fields.Char(string="IP Address")
    port = fields.Integer(string="Port", default=9100)

    # USB settings
    usb_vendor_id = fields.Char(string="USB Vendor ID")
    usb_product_id = fields.Char(string="USB Product ID")

    # Serial settings
    serial_port = fields.Char(string="Serial Port", help="e.g., /dev/ttyUSB0")
    serial_baudrate = fields.Integer(string="Baud Rate", default=9600)

    # CUPS settings
    cups_printer_name = fields.Char(string="CUPS Printer Name")

    # PrintNode settings
    printnode_printer_id = fields.Integer(string="PrintNode Printer ID")

    # Printer-specific
    printer_type = fields.Selection(
        [
            ("escpos", "ESC/POS (Receipt)"),
            ("star", "Star Micronics"),
            ("zpl", "Zebra ZPL (Label)"),
            ("pdf", "PDF/IPP"),
        ],
        string="Printer Type",
        default="escpos",
    )
    paper_width = fields.Integer(string="Paper Width (mm)", default=80)

    # State
    state = fields.Selection(
        [
            ("draft", "Not Connected"),
            ("connected", "Connected"),
            ("error", "Error"),
        ],
        default="draft",
        string="Status",
    )
    last_used = fields.Datetime(string="Last Used")
    error_message = fields.Text(string="Error Message")

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("identifier_gateway_unique", "unique(identifier, gateway_id)",
         "Device identifier must be unique per gateway"),
    ]

    def action_test_connection(self):
        """Test device connection."""
        self.ensure_one()

        try:
            if self.connection_type == "network":
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((self.ip_address, self.port or 9100))
                sock.close()

            elif self.connection_type == "cups":
                import subprocess

                cups_server = self.gateway_id.cups_server if self.gateway_id else "localhost"
                result = subprocess.run(
                    ["lpstat", "-h", cups_server, "-p", self.cups_printer_name],
                    capture_output=True,
                    timeout=5,
                )
                if result.returncode != 0:
                    raise Exception(result.stderr.decode())

            elif self.connection_type == "printnode":
                if not self.gateway_id or not self.gateway_id.printnode_api_key:
                    raise UserError("PrintNode API key required on gateway")

                response = requests.get(
                    f"https://api.printnode.com/printers/{self.printnode_printer_id}",
                    auth=(self.gateway_id.printnode_api_key, ""),
                    timeout=5,
                )
                response.raise_for_status()

            self.write({
                "state": "connected",
                "last_used": fields.Datetime.now(),
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
            self.write({"state": "error", "error_message": str(e)})
            raise UserError(f"Connection failed: {e}")

    def action_print_test_page(self):
        """Print a test page."""
        self.ensure_one()

        if self.device_type != "printer":
            raise UserError("Not a printer device")

        test_content = f"""
================================
IPAI IoT Bridge - Test Print
================================
Device: {self.name}
Type: {self.printer_type}
Date: {fields.Datetime.now()}
================================
If you can read this, the
printer is working correctly!
================================
"""

        try:
            self._send_to_printer(test_content.encode())

            self.write({
                "state": "connected",
                "last_used": fields.Datetime.now(),
            })

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Test Print",
                    "message": "Test page sent successfully",
                    "type": "success",
                },
            }

        except Exception as e:
            raise UserError(f"Print failed: {e}")

    def _send_to_printer(self, data):
        """Send data to printer based on connection type."""
        self.ensure_one()

        if self.connection_type == "network":
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.ip_address, self.port or 9100))
            sock.sendall(data)
            sock.close()

        elif self.connection_type == "cups":
            import subprocess
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(data)
                f.flush()

                cups_server = self.gateway_id.cups_server if self.gateway_id else "localhost"
                subprocess.run(
                    ["lp", "-h", cups_server, "-d", self.cups_printer_name, f.name],
                    check=True,
                    timeout=30,
                )

        elif self.connection_type == "printnode":
            import base64

            if not self.gateway_id or not self.gateway_id.printnode_api_key:
                raise UserError("PrintNode API key required")

            requests.post(
                "https://api.printnode.com/printjobs",
                auth=(self.gateway_id.printnode_api_key, ""),
                json={
                    "printerId": self.printnode_printer_id,
                    "title": "IPAI Print Job",
                    "contentType": "raw_base64",
                    "content": base64.b64encode(data).decode(),
                },
                timeout=30,
            )

        else:
            raise UserError(f"Unsupported connection type: {self.connection_type}")

    def print_receipt(self, content):
        """Print receipt content (ESC/POS formatted)."""
        self.ensure_one()

        if self.printer_type == "escpos":
            # Add ESC/POS commands
            data = b"\x1b\x40"  # Initialize
            data += content.encode() if isinstance(content, str) else content
            data += b"\x1d\x56\x00"  # Cut paper

        else:
            data = content.encode() if isinstance(content, str) else content

        self._send_to_printer(data)
        self.write({"last_used": fields.Datetime.now()})
