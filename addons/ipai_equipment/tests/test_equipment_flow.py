# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase, tagged
from odoo import fields
from datetime import datetime, timedelta


@tagged('post_install', '-at_install', 'ipai_equipment')
class TestIpaiEquipmentFlow(TransactionCase):
    """Test equipment booking and reservation workflow"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test equipment
        cls.equipment = cls.env['ipai.equipment.asset'].create({
            'name': 'Sony A7S3 Camera #1',
            'serial_number': 'SN001',
            'status': 'available',
            'condition': 'excellent',
        })

        cls.equipment2 = cls.env['ipai.equipment.asset'].create({
            'name': 'DJI Gimbal #1',
            'serial_number': 'SN002',
            'status': 'available',
            'condition': 'good',
        })

        # Create test employee
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Photographer',
        })

        cls.Booking = cls.env['ipai.equipment.booking']

    def test_01_equipment_creation(self):
        """Test equipment asset can be created"""
        equipment = self.env['ipai.equipment.asset'].create({
            'name': 'Test Camera',
            'serial_number': 'TEST001',
            'status': 'available',
        })

        self.assertTrue(equipment, "Equipment should be created")
        self.assertEqual(equipment.status, 'available')

    def test_02_booking_creation(self):
        """Test booking can be created"""
        booking = self.Booking.create({
            'asset_id': self.equipment.id,
            'borrower_id': self.employee.id,
            'date_start': datetime.now(),
            'date_stop': datetime.now() + timedelta(days=2),
        })

        self.assertTrue(booking, "Booking should be created")
        self.assertEqual(booking.state, 'reserved')

    def test_03_booking_checkout_return_flow(self):
        """Test complete booking workflow: reserve → check-out → return"""
        booking = self.Booking.create({
            'asset_id': self.equipment.id,
            'borrower_id': self.employee.id,
            'date_start': datetime.now(),
            'date_stop': datetime.now() + timedelta(days=3),
        })

        # Should start in reserved state
        self.assertEqual(booking.state, 'reserved')

        # Check out equipment
        if hasattr(booking, 'action_checkout'):
            booking.action_checkout()
            self.assertEqual(booking.state, 'checked_out')

        # Return equipment
        if hasattr(booking, 'action_return'):
            booking.action_return()
            self.assertEqual(booking.state, 'returned')

    def test_04_booking_overlap_prevention(self):
        """Test that overlapping bookings are prevented"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=5)

        # Create first booking
        booking1 = self.Booking.create({
            'asset_id': self.equipment.id,
            'borrower_id': self.employee.id,
            'date_start': start_date,
            'date_stop': end_date,
        })

        # Try to create overlapping booking - should fail
        with self.assertRaises(Exception):
            self.Booking.create({
                'asset_id': self.equipment.id,
                'borrower_id': self.employee.id,
                'date_start': start_date + timedelta(days=2),
                'date_stop': end_date + timedelta(days=2),
            })

    def test_05_multiple_bookings_different_equipment(self):
        """Test multiple bookings for different equipment"""
        start_date = datetime.now()

        booking1 = self.Booking.create({
            'asset_id': self.equipment.id,
            'borrower_id': self.employee.id,
            'date_start': start_date,
            'date_stop': start_date + timedelta(days=3),
        })

        booking2 = self.Booking.create({
            'asset_id': self.equipment2.id,
            'borrower_id': self.employee.id,
            'date_start': start_date,
            'date_stop': start_date + timedelta(days=3),
        })

        self.assertTrue(booking1)
        self.assertTrue(booking2)
        self.assertNotEqual(booking1.asset_id, booking2.asset_id)
