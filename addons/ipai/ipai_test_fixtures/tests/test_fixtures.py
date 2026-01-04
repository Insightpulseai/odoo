# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024 InsightPulseAI
"""
Test cases for IPAI Test Fixtures module.

Tests verify that factory methods work correctly.
"""
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "ipai_test_fixtures")
class TestFactoryMethods(TransactionCase):
    """Test factory method functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.factory = cls.env["ipai.test.factory"]

    def test_01_create_user_defaults(self):
        """Test user creation with defaults."""
        user = self.factory.create_user()

        self.assertTrue(user.name.startswith("Test User"))
        self.assertTrue(user.login.startswith("test_user_"))
        self.assertIn("@test.example.com", user.email)

    def test_02_create_user_roles(self):
        """Test user creation with different roles."""
        user_basic = self.factory.create_user(role="user")
        user_manager = self.factory.create_user(role="manager")
        user_admin = self.factory.create_user(role="admin")

        # Verify users were created
        self.assertTrue(user_basic)
        self.assertTrue(user_manager)
        self.assertTrue(user_admin)

    def test_03_create_employee(self):
        """Test employee creation."""
        employee = self.factory.create_employee()

        self.assertTrue(employee.name)
        self.assertTrue(employee.user_id)

    def test_04_create_employee_with_user(self):
        """Test employee creation with existing user."""
        user = self.factory.create_user(name="Specific User")
        employee = self.factory.create_employee(user=user)

        self.assertEqual(employee.user_id, user)
        self.assertEqual(employee.name, "Specific User")

    def test_05_create_department(self):
        """Test department creation."""
        dept = self.factory.create_department(name="Test Dept")

        self.assertEqual(dept.name, "Test Dept")

    def test_06_create_project(self):
        """Test project creation."""
        project = self.factory.create_project()

        self.assertTrue(project.name.startswith("Test Project"))

    def test_07_create_task(self):
        """Test task creation."""
        task = self.factory.create_task()

        self.assertTrue(task.name.startswith("Test Task"))
        self.assertTrue(task.project_id)
        self.assertTrue(task.date_deadline)

    def test_08_create_task_with_project(self):
        """Test task creation with existing project."""
        project = self.factory.create_project(name="My Project")
        task = self.factory.create_task(project=project)

        self.assertEqual(task.project_id, project)

    def test_09_get_admin_user(self):
        """Test getting admin user."""
        admin = self.factory.get_admin_user()

        self.assertTrue(admin)
        self.assertEqual(admin.login, "admin")
