# -*- coding: utf-8 -*-
# Copyright 2026 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestIPAISampleMetrics(TransactionCase):
    """Test cases for ipai.sample.metric model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MetricModel = cls.env["ipai.sample.metric"]

    def test_create_metric(self):
        """Test basic metric creation."""
        rec = self.MetricModel.create({
            "name": "Test Metric",
            "code": "TEST",
            "value": 50.0,
            "unit": "percent",
        })
        self.assertTrue(rec.id)
        self.assertEqual(rec.name, "Test Metric")
        self.assertEqual(rec.code, "TEST")
        self.assertEqual(rec.value, 50.0)
        self.assertFalse(rec.is_alert)  # 50% should not be flagged

    def test_is_alert_low_percent(self):
        """Test that low percentage triggers alert."""
        rec = self.MetricModel.create({
            "name": "Low Conversion",
            "code": "LOW_CONV",
            "value": 5.0,
            "unit": "percent",
        })
        self.assertTrue(rec.is_alert)  # Below 10% threshold

    def test_is_alert_high_percent(self):
        """Test that high percentage triggers alert."""
        rec = self.MetricModel.create({
            "name": "High Conversion",
            "code": "HIGH_CONV",
            "value": 98.0,
            "unit": "percent",
        })
        self.assertTrue(rec.is_alert)  # Above 95% threshold

    def test_is_alert_count_unit(self):
        """Test that count unit never triggers alert."""
        rec = self.MetricModel.create({
            "name": "Traffic Count",
            "code": "TRAFFIC",
            "value": 5.0,  # Low value but count unit
            "unit": "count",
        })
        self.assertFalse(rec.is_alert)

    def test_create_from_payload(self):
        """Test API helper create_from_payload."""
        payload = {
            "name": "API Test Metric",
            "code": "API_TEST",
            "value": 75.5,
            "unit": "percent",
            "notes": "Created via API",
        }
        metric_id = self.MetricModel.create_from_payload(payload)
        self.assertTrue(metric_id)

        rec = self.MetricModel.browse(metric_id)
        self.assertEqual(rec.name, "API Test Metric")
        self.assertEqual(rec.value, 75.5)

    def test_create_from_payload_missing_required(self):
        """Test that create_from_payload raises on missing required fields."""
        payload = {
            "name": "Incomplete",
            # Missing code and value
        }
        with self.assertRaises(ValueError) as cm:
            self.MetricModel.create_from_payload(payload)
        self.assertIn("code", str(cm.exception))
        self.assertIn("value", str(cm.exception))

    def test_get_metrics(self):
        """Test API helper get_metrics."""
        # Create test data
        self.MetricModel.create({
            "name": "Metric A",
            "code": "METRIC_A",
            "value": 30.0,
            "unit": "percent",
        })
        self.MetricModel.create({
            "name": "Metric B",
            "code": "METRIC_B",
            "value": 60.0,
            "unit": "percent",
        })

        # Get all metrics with filter
        results = self.MetricModel.get_metrics(
            filters=[("code", "=", "METRIC_A")]
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["code"], "METRIC_A")
        self.assertEqual(results[0]["value"], 30.0)

    def test_get_metrics_no_filter(self):
        """Test get_metrics without filter returns records."""
        self.MetricModel.create({
            "name": "Unfiltered Metric",
            "code": "UNFILTERED",
            "value": 45.0,
            "unit": "count",
        })
        results = self.MetricModel.get_metrics()
        self.assertTrue(len(results) >= 1)

    def test_active_field(self):
        """Test that active field defaults to True."""
        rec = self.MetricModel.create({
            "name": "Active Test",
            "code": "ACTIVE_TEST",
            "value": 50.0,
            "unit": "percent",
        })
        self.assertTrue(rec.active)

        # Archive the record
        rec.active = False
        self.assertFalse(rec.active)
