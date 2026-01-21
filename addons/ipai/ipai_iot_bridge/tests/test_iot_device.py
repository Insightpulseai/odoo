# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase


class TestIotDevice(TransactionCase):
    """Test cases for IoT Bridge module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Device = cls.env["ipai.iot.device"]
        cls.Reading = cls.env["ipai.iot.reading"]

    def test_device_creation(self):
        """Test creating an IoT device."""
        device = self.Device.create(
            {
                "name": "Test Sensor",
                "device_code": "SENSOR001",
                "device_type": "sensor",
                "protocol": "http",
            }
        )
        self.assertEqual(device.name, "Test Sensor")
        self.assertEqual(device.state, "draft")

    def test_device_activation(self):
        """Test activating a device."""
        device = self.Device.create(
            {
                "name": "Test Device",
                "device_code": "DEV001",
                "device_type": "sensor",
                "protocol": "mqtt",
            }
        )
        device.action_activate()
        self.assertEqual(device.state, "active")

    def test_reading_creation(self):
        """Test creating a reading."""
        device = self.Device.create(
            {
                "name": "Temp Sensor",
                "device_code": "TEMP001",
                "device_type": "sensor",
                "protocol": "mqtt",
            }
        )
        reading = self.Reading.create_reading(
            device_code="TEMP001",
            reading_type="temperature",
            value=25.5,
            unit="°C",
        )
        self.assertEqual(reading.value_float, 25.5)
        self.assertEqual(reading.unit, "°C")

    def test_reading_count(self):
        """Test reading count computation."""
        device = self.Device.create(
            {
                "name": "Counter Device",
                "device_code": "COUNT001",
                "device_type": "sensor",
                "protocol": "http",
            }
        )
        # Create multiple readings
        for i in range(5):
            self.Reading.create_reading(
                device_code="COUNT001",
                reading_type="count",
                value=i,
            )
        device.invalidate_recordset(["reading_count"])
        self.assertEqual(device.reading_count, 5)

    def test_unique_device_code(self):
        """Test that device codes must be unique."""
        self.Device.create(
            {
                "name": "Device 1",
                "device_code": "UNIQUE001",
                "device_type": "sensor",
                "protocol": "http",
            }
        )
        with self.assertRaises(Exception):
            self.Device.create(
                {
                    "name": "Device 2",
                    "device_code": "UNIQUE001",
                    "device_type": "sensor",
                    "protocol": "http",
                }
            )
