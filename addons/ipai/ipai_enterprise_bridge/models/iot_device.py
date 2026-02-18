# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class IotDevice(models.Model):
    _name = "ipai.iot.device"
    _description = "IoT Device Registry"
    _order = "name"

    name = fields.Char(required=True, string="Device Name")
    device_type = fields.Selection(
        [
            ("printer", "Printer"),
            ("scale", "Scale"),
            ("drawer", "Cash Drawer"),
            ("display", "Customer Display"),
            ("scanner", "Barcode Scanner"),
            ("payment", "Payment Terminal"),
            ("other", "Other"),
        ],
        string="Device Type",
        required=True,
        default="other",
    )
    identifier = fields.Char(
        string="Device ID",
        help="Unique hardware identifier (MAC, serial, etc.)",
    )
    mqtt_topic = fields.Char(
        string="MQTT Topic",
        help="Topic for device communication",
    )
    status = fields.Selection(
        [
            ("online", "Online"),
            ("offline", "Offline"),
            ("error", "Error"),
            ("unknown", "Unknown"),
        ],
        string="Status",
        default="unknown",
        readonly=True,
    )
    last_seen = fields.Datetime(
        string="Last Seen",
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    notes = fields.Text(string="Notes")

    # Connection details
    connection_type = fields.Selection(
        [
            ("mqtt", "MQTT"),
            ("websocket", "WebSocket"),
            ("http", "HTTP API"),
            ("usb", "USB Direct"),
        ],
        string="Connection Type",
        default="mqtt",
    )
    connection_url = fields.Char(string="Connection URL")

    _sql_constraints = [
        ("identifier_uniq", "unique(identifier)", "Device identifier must be unique!"),
    ]

    def action_ping(self):
        """Send ping command to device."""
        self.ensure_one()
        bridge = self.env["ipai.iot.mqtt.bridge"]
        return bridge.send_command(self, {"action": "ping"})

    def action_refresh_status(self):
        """Request status update from device."""
        self.ensure_one()
        bridge = self.env["ipai.iot.mqtt.bridge"]
        return bridge.send_command(self, {"action": "status"})

    @api.model
    def update_device_status(self, identifier, status, timestamp=None):
        """Called by MQTT callback to update device status."""
        device = self.search([("identifier", "=", identifier)], limit=1)
        if device:
            vals = {"status": status}
            if timestamp:
                vals["last_seen"] = timestamp
            else:
                vals["last_seen"] = fields.Datetime.now()
            device.write(vals)
            return True
        return False
