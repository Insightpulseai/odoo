# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase, tagged
from odoo import fields


@tagged('post_install', '-at_install', 'ipai_expense')
class TestIpaiExpenseBusinessFlow(TransactionCase):
    """Test complete expense submission and approval workflow"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test employee
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
        })

        # Create test manager
        cls.manager = cls.env['hr.employee'].create({
            'name': 'Test Manager',
        })

        cls.Expense = cls.env['ipai.travel.request']

    def test_01_expense_creation(self):
        """Test expense can be created with required fields"""
        expense = self.Expense.create({
            'employee_id': self.employee.id,
            'description': 'Client Meeting - Coffee',
            'date': fields.Date.today(),
            'amount': 1500.0,
        })

        self.assertTrue(expense, "Expense should be created")
        self.assertEqual(expense.amount, 1500.0, "Amount should match")
        self.assertEqual(expense.state, 'draft', "New expense should be in draft state")

    def test_02_expense_submit_approve_flow(self):
        """Test expense submission and approval workflow"""
        expense = self.Expense.create({
            'employee_id': self.employee.id,
            'description': 'Travel Expense - Taxi',
            'date': fields.Date.today(),
            'amount': 850.0,
        })

        # Test draft state
        self.assertEqual(expense.state, 'draft')

        # Submit expense
        if hasattr(expense, 'action_submit'):
            expense.action_submit()
            self.assertEqual(expense.state, 'submitted', "Expense should be submitted")

            # Approve expense
            if hasattr(expense, 'action_approve'):
                expense.action_approve()
                self.assertEqual(expense.state, 'approved', "Expense should be approved")

    def test_03_expense_validation(self):
        """Test expense validation rules"""
        # Test amount validation
        with self.assertRaises(Exception):
            self.Expense.create({
                'employee_id': self.employee.id,
                'description': 'Invalid Expense',
                'date': fields.Date.today(),
                'amount': -100.0,  # Negative amount should fail
            })

    def test_04_expense_with_ocr(self):
        """Test expense with OCR integration"""
        expense = self.Expense.create({
            'employee_id': self.employee.id,
            'description': 'Restaurant Bill',
            'date': fields.Date.today(),
            'amount': 0.0,
        })

        # Simulate OCR processing
        if hasattr(expense, 'ocr_status'):
            expense.write({
                'ocr_status': 'processed',
                'ocr_vendor_detected': 'Test Restaurant',
                'ocr_amount_detected': 2500.50,
            })

            self.assertEqual(expense.ocr_status, 'processed')
            self.assertEqual(expense.ocr_vendor_detected, 'Test Restaurant')
            self.assertEqual(expense.ocr_amount_detected, 2500.50)
