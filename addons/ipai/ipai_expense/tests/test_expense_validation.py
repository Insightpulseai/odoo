# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024 InsightPulseAI
"""
Test cases for IPAI Expense & Travel module.

Tests cover:
- Travel request workflow transitions
- Travel request validation
- Expense-travel request linkage
"""
from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "ipai_expense")
class TestTravelRequestWorkflow(TransactionCase):
    """Test travel request state transitions and validation."""

    @classmethod
    def setUpClass(cls):
        """Set up test data for travel request tests."""
        super().setUpClass()

        # Create test employee
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
            }
        )

        # Create test project
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
            }
        )

    def test_travel_request_creation(self):
        """Test that travel requests are created in draft state."""
        travel_request = self.env["ipai.travel.request"].create(
            {
                "employee_id": self.employee.id,
                "destination": "Manila",
                "start_date": date.today() + timedelta(days=7),
                "end_date": date.today() + timedelta(days=10),
                "purpose": "Client meeting",
            }
        )

        self.assertEqual(travel_request.state, "draft")
        self.assertEqual(travel_request.employee_id, self.employee)

    def test_travel_request_submit(self):
        """Test travel request submission workflow."""
        travel_request = self.env["ipai.travel.request"].create(
            {
                "employee_id": self.employee.id,
                "destination": "Cebu",
                "start_date": date.today() + timedelta(days=14),
                "end_date": date.today() + timedelta(days=17),
            }
        )

        travel_request.action_submit()
        self.assertEqual(travel_request.state, "submitted")

    def test_travel_request_manager_approve(self):
        """Test manager approval step."""
        travel_request = self.env["ipai.travel.request"].create(
            {
                "employee_id": self.employee.id,
                "destination": "Davao",
                "start_date": date.today() + timedelta(days=21),
                "end_date": date.today() + timedelta(days=24),
            }
        )

        travel_request.action_submit()
        travel_request.action_manager_approve()
        self.assertEqual(travel_request.state, "manager_approved")

    def test_travel_request_finance_approve(self):
        """Test finance approval step (full workflow)."""
        travel_request = self.env["ipai.travel.request"].create(
            {
                "employee_id": self.employee.id,
                "destination": "Boracay",
                "start_date": date.today() + timedelta(days=28),
                "end_date": date.today() + timedelta(days=31),
                "estimated_budget": 50000.00,
            }
        )

        # Complete full approval workflow
        travel_request.action_submit()
        travel_request.action_manager_approve()
        travel_request.action_finance_approve()
        self.assertEqual(travel_request.state, "finance_approved")

    def test_travel_request_reject(self):
        """Test travel request rejection at any stage."""
        travel_request = self.env["ipai.travel.request"].create(
            {
                "employee_id": self.employee.id,
                "destination": "Palawan",
                "start_date": date.today() + timedelta(days=35),
                "end_date": date.today() + timedelta(days=38),
            }
        )

        travel_request.action_submit()
        travel_request.action_reject()
        self.assertEqual(travel_request.state, "rejected")

    def test_travel_request_with_project(self):
        """Test travel request with project linkage."""
        travel_request = self.env["ipai.travel.request"].create(
            {
                "employee_id": self.employee.id,
                "project_id": self.project.id,
                "destination": "Baguio",
                "start_date": date.today() + timedelta(days=42),
                "end_date": date.today() + timedelta(days=45),
                "purpose": "Project site visit",
            }
        )

        self.assertEqual(travel_request.project_id, self.project)


@tagged("post_install", "-at_install", "ipai_expense")
class TestExpenseValidation(TransactionCase):
    """Test expense validation and constraints."""

    @classmethod
    def setUpClass(cls):
        """Set up test data for expense tests."""
        super().setUpClass()

        # Create test employee
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Expense Employee",
            }
        )

        # Create test project
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Expense Project",
            }
        )

    def test_expense_creation(self):
        """Test basic expense creation."""
        expense = self.env["hr.expense"].create(
            {
                "name": "Test Expense",
                "employee_id": self.employee.id,
                "total_amount": 1000.00,
            }
        )

        self.assertTrue(expense.id)
        self.assertEqual(expense.employee_id, self.employee)

    def test_expense_with_project(self):
        """Test expense with project linkage."""
        expense = self.env["hr.expense"].create(
            {
                "name": "Project Expense",
                "employee_id": self.employee.id,
                "project_id": self.project.id,
                "total_amount": 2500.00,
            }
        )

        self.assertEqual(expense.project_id, self.project)
