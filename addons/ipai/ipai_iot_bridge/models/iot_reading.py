# -*- coding: utf-8 -*-
"""
IoT Reading - Device Data Collection

Stores and manages IoT sensor readings and events.
"""
from odoo import api, fields, models


class IpaiIotReading(models.Model):
    """IoT Device Reading/Event."""

    _name = "ipai.iot.reading"
    _description = "IoT Reading"
    _order = "timestamp desc"

    device_id = fields.Many2one(
        "ipai.iot.device",
        string="Device",
        required=True,
        ondelete="cascade",
        index=True,
    )
    timestamp = fields.Datetime(
        string="Timestamp",
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    reading_type = fields.Selection(
        [
            ("temperature", "Temperature"),
            ("humidity", "Humidity"),
            ("pressure", "Pressure"),
            ("light", "Light"),
            ("motion", "Motion"),
            ("power", "Power"),
            ("voltage", "Voltage"),
            ("current", "Current"),
            ("count", "Count"),
            ("status", "Status"),
            ("event", "Event"),
            ("other", "Other"),
        ],
        string="Reading Type",
        required=True,
        default="other",
    )
    value_float = fields.Float(
        string="Numeric Value",
        digits=(16, 4),
    )
    value_string = fields.Char(
        string="String Value",
    )
    value_boolean = fields.Boolean(
        string="Boolean Value",
    )
    unit = fields.Char(
        string="Unit",
        help="Unit of measurement (e.g., °C, %, W)",
    )
    raw_data = fields.Text(
        string="Raw Data",
        help="Raw JSON or text data from device",
    )

    # Alerts
    is_alert = fields.Boolean(
        string="Is Alert",
        default=False,
    )
    alert_level = fields.Selection(
        [
            ("info", "Info"),
            ("warning", "Warning"),
            ("critical", "Critical"),
        ],
        string="Alert Level",
    )
    alert_message = fields.Char(
        string="Alert Message",
    )
    alert_acknowledged = fields.Boolean(
        string="Acknowledged",
        default=False,
    )
    acknowledged_by = fields.Many2one(
        "res.users",
        string="Acknowledged By",
    )
    acknowledged_at = fields.Datetime(
        string="Acknowledged At",
    )

    @api.model
    def create_reading(self, device_code, reading_type, value, **kwargs):
        """Create a reading for a device by code.

        Args:
            device_code: Device code identifier
            reading_type: Type of reading
            value: Reading value (auto-detected type)
            **kwargs: Additional fields

        Returns:
            recordset: Created reading record
        """
        Device = self.env["ipai.iot.device"]
        device = Device.search([("device_code", "=", device_code)], limit=1)

        if not device:
            raise ValueError(f"Device not found: {device_code}")

        vals = {
            "device_id": device.id,
            "reading_type": reading_type,
            "timestamp": kwargs.get("timestamp", fields.Datetime.now()),
        }

        # Auto-detect value type
        if isinstance(value, bool):
            vals["value_boolean"] = value
        elif isinstance(value, (int, float)):
            vals["value_float"] = value
        else:
            vals["value_string"] = str(value)

        # Add optional fields
        for field in ["unit", "raw_data", "is_alert", "alert_level", "alert_message"]:
            if field in kwargs:
                vals[field] = kwargs[field]

        reading = self.create(vals)

        # Update device last_seen
        device.write({"last_seen": vals["timestamp"]})

        return reading

    def action_acknowledge(self):
        """Acknowledge an alert."""
        for reading in self.filtered("is_alert"):
            reading.write(
                {
                    "alert_acknowledged": True,
                    "acknowledged_by": self.env.user.id,
                    "acknowledged_at": fields.Datetime.now(),
                }
            )


class IpaiIotAlert(models.Model):
    """IoT Alert Configuration."""

    _name = "ipai.iot.alert"
    _description = "IoT Alert Rule"

    name = fields.Char(
        string="Alert Name",
        required=True,
    )
    device_id = fields.Many2one(
        "ipai.iot.device",
        string="Device",
        help="Leave empty for all devices",
    )
    reading_type = fields.Selection(
        [
            ("temperature", "Temperature"),
            ("humidity", "Humidity"),
            ("pressure", "Pressure"),
            ("power", "Power"),
            ("voltage", "Voltage"),
            ("other", "Other"),
        ],
        string="Reading Type",
        required=True,
    )
    condition = fields.Selection(
        [
            ("gt", "Greater Than"),
            ("gte", "Greater Than or Equal"),
            ("lt", "Less Than"),
            ("lte", "Less Than or Equal"),
            ("eq", "Equal To"),
            ("neq", "Not Equal To"),
        ],
        string="Condition",
        required=True,
    )
    threshold = fields.Float(
        string="Threshold",
        required=True,
    )
    alert_level = fields.Selection(
        [
            ("info", "Info"),
            ("warning", "Warning"),
            ("critical", "Critical"),
        ],
        string="Alert Level",
        default="warning",
    )
    message_template = fields.Char(
        string="Message Template",
        help="Use {device}, {value}, {threshold} placeholders",
        default="{device} {reading_type}: {value} {condition} {threshold}",
    )
    is_active = fields.Boolean(
        string="Active",
        default=True,
    )
    notify_user_ids = fields.Many2many(
        "res.users",
        string="Notify Users",
    )
