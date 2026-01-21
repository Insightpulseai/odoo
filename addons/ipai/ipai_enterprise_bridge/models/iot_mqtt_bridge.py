# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import json
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    _logger.warning("paho-mqtt not installed. IoT MQTT bridge disabled.")


class IotMqttBridge(models.AbstractModel):
    _name = "ipai.iot.mqtt.bridge"
    _description = "IoT MQTT Bridge"

    @api.model
    def _get_mqtt_config(self):
        """Get MQTT configuration from ir.config_parameter."""
        params = self.env["ir.config_parameter"].sudo()
        return {
            "broker": params.get_param("ipai.iot.mqtt.broker", "localhost"),
            "port": int(params.get_param("ipai.iot.mqtt.port", 1883)),
            "username": params.get_param("ipai.iot.mqtt.username", ""),
            "password": params.get_param("ipai.iot.mqtt.password", ""),
        }

    @api.model
    def _connect_mqtt(self):
        """Create and connect MQTT client."""
        if not MQTT_AVAILABLE:
            _logger.error("paho-mqtt not available")
            return None

        config = self._get_mqtt_config()
        client = mqtt.Client()

        if config.get("username"):
            client.username_pw_set(config["username"], config.get("password", ""))

        try:
            client.connect(config["broker"], config["port"], keepalive=60)
            return client
        except Exception as e:
            _logger.error("Failed to connect to MQTT broker: %s", e)
            return None

    @api.model
    def send_command(self, device, command):
        """Send command to IoT device via MQTT.

        Args:
            device: ipai.iot.device record
            command: dict with command data

        Returns:
            bool: True if sent successfully
        """
        if not device.mqtt_topic:
            _logger.warning("Device %s has no MQTT topic configured", device.name)
            return False

        client = self._connect_mqtt()
        if not client:
            return False

        try:
            payload = json.dumps(command)
            result = client.publish(device.mqtt_topic, payload)
            client.disconnect()
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            _logger.error("Failed to send MQTT command: %s", e)
            return False

    @api.model
    def broadcast_command(self, device_type, command):
        """Broadcast command to all devices of a type.

        Args:
            device_type: str device type (printer, scale, etc.)
            command: dict with command data

        Returns:
            int: Number of devices that received the command
        """
        devices = self.env["ipai.iot.device"].search([
            ("device_type", "=", device_type),
            ("status", "=", "online"),
        ])
        sent = 0
        for device in devices:
            if self.send_command(device, command):
                sent += 1
        return sent
