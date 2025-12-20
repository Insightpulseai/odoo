# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024 InsightPulseAI
"""
Test cases for IPAI Equipment Management module.

Tests cover:
- Equipment asset lifecycle (creation, status changes)
- Equipment booking workflow (reserve, checkout, return)
- Booking conflict detection
- Incident reporting
"""
from datetime import datetime, timedelta

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "ipai_equipment")
class TestEquipmentAsset(TransactionCase):
    """Test equipment asset management."""

    @classmethod
    def setUpClass(cls):
        """Set up test data for equipment asset tests."""
        super().setUpClass()

    def test_asset_creation(self):
        """Test that assets are created with correct defaults."""
        asset = self.env["ipai.equipment.asset"].create(
            {
                "name": "Test Camera",
            }
        )

        self.assertEqual(asset.condition, "good")
        self.assertEqual(asset.status, "available")
        self.assertTrue(asset.name)

    def test_asset_condition_states(self):
        """Test asset condition can be set to all valid states."""
        conditions = ["new", "good", "used", "damaged"]

        for condition in conditions:
            asset = self.env["ipai.equipment.asset"].create(
                {
                    "name": f"Asset {condition}",
                    "condition": condition,
                }
            )
            self.assertEqual(asset.condition, condition)

    def test_asset_status_states(self):
        """Test asset status can be set to all valid states."""
        statuses = ["available", "reserved", "checked_out", "maintenance"]

        for status in statuses:
            asset = self.env["ipai.equipment.asset"].create(
                {
                    "name": f"Asset {status}",
                    "status": status,
                }
            )
            self.assertEqual(asset.status, status)

    def test_asset_with_serial_number(self):
        """Test asset creation with serial number."""
        asset = self.env["ipai.equipment.asset"].create(
            {
                "name": "Laptop Dell XPS",
                "serial_number": "DL-2024-001",
                "condition": "new",
            }
        )

        self.assertEqual(asset.serial_number, "DL-2024-001")


@tagged("post_install", "-at_install", "ipai_equipment")
class TestEquipmentBooking(TransactionCase):
    """Test equipment booking workflow."""

    @classmethod
    def setUpClass(cls):
        """Set up test data for booking tests."""
        super().setUpClass()

        # Create test asset
        cls.asset = cls.env["ipai.equipment.asset"].create(
            {
                "name": "Test Booking Asset",
                "condition": "good",
                "status": "available",
            }
        )

        # Get demo user for borrower
        cls.borrower = cls.env.ref("base.user_admin")

    def test_booking_creation(self):
        """Test booking is created in draft state."""
        booking = self.env["ipai.equipment.booking"].create(
            {
                "asset_id": self.asset.id,
                "borrower_id": self.borrower.id,
                "start_datetime": datetime.now() + timedelta(days=1),
                "end_datetime": datetime.now() + timedelta(days=3),
            }
        )

        self.assertEqual(booking.state, "draft")
        self.assertEqual(booking.asset_id, self.asset)

    def test_booking_reserve(self):
        """Test booking reservation updates asset status."""
        # Create a fresh asset for this test
        asset = self.env["ipai.equipment.asset"].create(
            {
                "name": "Reserve Test Asset",
                "status": "available",
            }
        )

        booking = self.env["ipai.equipment.booking"].create(
            {
                "asset_id": asset.id,
                "borrower_id": self.borrower.id,
                "start_datetime": datetime.now() + timedelta(days=7),
                "end_datetime": datetime.now() + timedelta(days=10),
            }
        )

        booking.action_reserve()

        self.assertEqual(booking.state, "reserved")
        self.assertEqual(asset.status, "reserved")

    def test_booking_checkout(self):
        """Test checkout updates asset status."""
        asset = self.env["ipai.equipment.asset"].create(
            {
                "name": "Checkout Test Asset",
                "status": "available",
            }
        )

        booking = self.env["ipai.equipment.booking"].create(
            {
                "asset_id": asset.id,
                "borrower_id": self.borrower.id,
                "start_datetime": datetime.now() + timedelta(days=14),
                "end_datetime": datetime.now() + timedelta(days=17),
            }
        )

        booking.action_reserve()
        booking.action_check_out()

        self.assertEqual(booking.state, "checked_out")
        self.assertEqual(asset.status, "checked_out")

    def test_booking_return(self):
        """Test return releases asset."""
        asset = self.env["ipai.equipment.asset"].create(
            {
                "name": "Return Test Asset",
                "status": "available",
            }
        )

        booking = self.env["ipai.equipment.booking"].create(
            {
                "asset_id": asset.id,
                "borrower_id": self.borrower.id,
                "start_datetime": datetime.now() + timedelta(days=21),
                "end_datetime": datetime.now() + timedelta(days=24),
            }
        )

        # Complete full workflow
        booking.action_reserve()
        booking.action_check_out()
        booking.action_return()

        self.assertEqual(booking.state, "returned")
        self.assertEqual(asset.status, "available")

    def test_booking_cancel(self):
        """Test cancellation releases asset."""
        asset = self.env["ipai.equipment.asset"].create(
            {
                "name": "Cancel Test Asset",
                "status": "available",
            }
        )

        booking = self.env["ipai.equipment.booking"].create(
            {
                "asset_id": asset.id,
                "borrower_id": self.borrower.id,
                "start_datetime": datetime.now() + timedelta(days=28),
                "end_datetime": datetime.now() + timedelta(days=31),
            }
        )

        booking.action_reserve()
        booking.action_cancel()

        self.assertEqual(booking.state, "cancelled")
        self.assertEqual(asset.status, "available")

    def test_booking_conflict_detection(self):
        """Test that overlapping bookings are rejected."""
        asset = self.env["ipai.equipment.asset"].create(
            {
                "name": "Conflict Test Asset",
                "status": "available",
            }
        )

        # Create first booking
        booking1 = self.env["ipai.equipment.booking"].create(
            {
                "asset_id": asset.id,
                "borrower_id": self.borrower.id,
                "start_datetime": datetime.now() + timedelta(days=35),
                "end_datetime": datetime.now() + timedelta(days=40),
            }
        )
        booking1.action_reserve()

        # Try to create overlapping booking - should raise ValueError
        try:
            self.env["ipai.equipment.booking"].create(
                {
                    "asset_id": asset.id,
                    "borrower_id": self.borrower.id,
                    "start_datetime": datetime.now() + timedelta(days=37),
                    "end_datetime": datetime.now() + timedelta(days=42),
                    "state": "reserved",
                }
            )
            self.fail("Expected ValueError for overlapping booking")
        except ValueError:
            pass  # Expected behavior


@tagged("post_install", "-at_install", "ipai_equipment")
class TestEquipmentIncident(TransactionCase):
    """Test equipment incident reporting."""

    @classmethod
    def setUpClass(cls):
        """Set up test data for incident tests."""
        super().setUpClass()

        cls.asset = cls.env["ipai.equipment.asset"].create(
            {
                "name": "Incident Test Asset",
            }
        )

        cls.reporter = cls.env.ref("base.user_admin")

    def test_incident_creation(self):
        """Test incident is created with defaults."""
        incident = self.env["ipai.equipment.incident"].create(
            {
                "name": "Scratched lens",
                "asset_id": self.asset.id,
                "reported_by": self.reporter.id,
            }
        )

        self.assertEqual(incident.severity, "low")
        self.assertEqual(incident.status, "open")

    def test_incident_severity_levels(self):
        """Test incident severity levels."""
        severities = ["low", "medium", "high"]

        for severity in severities:
            incident = self.env["ipai.equipment.incident"].create(
                {
                    "name": f"Incident {severity}",
                    "asset_id": self.asset.id,
                    "reported_by": self.reporter.id,
                    "severity": severity,
                }
            )
            self.assertEqual(incident.severity, severity)

    def test_incident_status_tracking(self):
        """Test incident status can be updated."""
        incident = self.env["ipai.equipment.incident"].create(
            {
                "name": "Status tracking test",
                "asset_id": self.asset.id,
                "reported_by": self.reporter.id,
            }
        )

        # Update to in_progress
        incident.status = "in_progress"
        self.assertEqual(incident.status, "in_progress")

        # Update to resolved
        incident.status = "resolved"
        self.assertEqual(incident.status, "resolved")
