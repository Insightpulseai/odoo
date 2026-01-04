# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024 InsightPulseAI
"""
Test Factory Methods for IPAI Modules.

Provides reusable factory methods for creating test data with sensible defaults.
These factories are designed to be used in TransactionCase test classes.

Usage in tests:
    from odoo.tests.common import TransactionCase

    class TestMyModule(TransactionCase):
        @classmethod
        def setUpClass(cls):
            super().setUpClass()
            cls.factory = cls.env['ipai.test.factory']

        def test_something(self):
            user = self.factory.create_user(role='manager')
            employee = self.factory.create_employee(user=user)
            project = self.factory.create_project()
"""
import uuid
from datetime import date, timedelta

from odoo import api, models


class IpaiTestFactory(models.AbstractModel):
    """Factory methods for creating test data."""

    _name = "ipai.test.factory"
    _description = "IPAI Test Data Factory"

    # -------------------------------------------------------------------------
    # User & Employee Factories
    # -------------------------------------------------------------------------

    @api.model
    def create_user(self, name=None, login=None, role="user", **kwargs):
        """
        Create a test user with the specified role.

        Args:
            name: User name (auto-generated if not provided)
            login: Login (auto-generated if not provided)
            role: 'user', 'manager', or 'admin'
            **kwargs: Additional fields to set

        Returns:
            res.users record
        """
        unique_id = str(uuid.uuid4())[:8]
        name = name or f"Test User {unique_id}"
        login = login or f"test_user_{unique_id}"

        # Determine groups based on role
        groups = [(4, self.env.ref("base.group_user").id)]
        if role == "manager":
            groups.append((4, self.env.ref("base.group_system").id))
        elif role == "admin":
            groups.append((4, self.env.ref("base.group_erp_manager").id))

        values = {
            "name": name,
            "login": login,
            "email": f"{login}@test.example.com",
            "groups_id": groups,
            **kwargs,
        }

        return self.env["res.users"].create(values)

    @api.model
    def create_employee(self, user=None, name=None, department=None, **kwargs):
        """
        Create a test employee.

        Args:
            user: res.users record (creates one if not provided)
            name: Employee name (uses user name if not provided)
            department: hr.department record
            **kwargs: Additional fields to set

        Returns:
            hr.employee record
        """
        if not user:
            user = self.create_user()

        values = {
            "name": name or user.name,
            "user_id": user.id,
            **kwargs,
        }

        if department:
            values["department_id"] = department.id

        return self.env["hr.employee"].create(values)

    @api.model
    def create_department(self, name=None, manager=None, **kwargs):
        """
        Create a test department.

        Args:
            name: Department name (auto-generated if not provided)
            manager: hr.employee record to set as manager
            **kwargs: Additional fields to set

        Returns:
            hr.department record
        """
        unique_id = str(uuid.uuid4())[:8]
        values = {
            "name": name or f"Test Department {unique_id}",
            **kwargs,
        }

        if manager:
            values["manager_id"] = manager.id

        return self.env["hr.department"].create(values)

    # -------------------------------------------------------------------------
    # Project & Task Factories
    # -------------------------------------------------------------------------

    @api.model
    def create_project(self, name=None, user=None, **kwargs):
        """
        Create a test project.

        Args:
            name: Project name (auto-generated if not provided)
            user: res.users to assign as project manager
            **kwargs: Additional fields to set

        Returns:
            project.project record
        """
        unique_id = str(uuid.uuid4())[:8]
        values = {
            "name": name or f"Test Project {unique_id}",
            **kwargs,
        }

        if user:
            values["user_id"] = user.id

        return self.env["project.project"].create(values)

    @api.model
    def create_task(
        self,
        project=None,
        name=None,
        user=None,
        deadline_days=7,
        **kwargs,
    ):
        """
        Create a test task.

        Args:
            project: project.project record (creates one if not provided)
            name: Task name (auto-generated if not provided)
            user: res.users to assign
            deadline_days: Days from today for deadline (default 7)
            **kwargs: Additional fields to set

        Returns:
            project.task record
        """
        if not project:
            project = self.create_project()

        unique_id = str(uuid.uuid4())[:8]
        values = {
            "name": name or f"Test Task {unique_id}",
            "project_id": project.id,
            "date_deadline": date.today() + timedelta(days=deadline_days),
            **kwargs,
        }

        if user:
            values["user_ids"] = [(4, user.id)]

        return self.env["project.task"].create(values)

    # -------------------------------------------------------------------------
    # Finance Factories
    # -------------------------------------------------------------------------

    @api.model
    def create_logframe(self, level="output", name=None, code=None, **kwargs):
        """
        Create a test finance logframe entry.

        Args:
            level: Logframe level (goal, outcome, im1, im2, output, activity_im1, activity_im2)
            name: Entry name (auto-generated if not provided)
            code: Entry code (auto-generated if not provided)
            **kwargs: Additional fields to set

        Returns:
            ipai.finance.logframe record (if module installed)
        """
        if "ipai.finance.logframe" not in self.env:
            return None

        unique_id = str(uuid.uuid4())[:8]
        values = {
            "level": level,
            "name": name or f"Test {level.title()} {unique_id}",
            "code": code or f"T{unique_id[:4].upper()}",
            **kwargs,
        }

        return self.env["ipai.finance.logframe"].create(values)

    @api.model
    def create_bir_schedule(
        self,
        name=None,
        period=None,
        filing_deadline=None,
        supervisor=None,
        reviewer=None,
        approver=None,
        **kwargs,
    ):
        """
        Create a test BIR schedule entry.

        Args:
            name: Schedule name (auto-generated if not provided)
            period: Period covered string (e.g., "Dec 2025")
            filing_deadline: Filing deadline date (default: 30 days from today)
            supervisor: res.users for supervisor
            reviewer: res.users for reviewer
            approver: res.users for approver
            **kwargs: Additional fields to set

        Returns:
            ipai.finance.bir_schedule record (if module installed)
        """
        if "ipai.finance.bir_schedule" not in self.env:
            return None

        unique_id = str(uuid.uuid4())[:8]
        filing_deadline = filing_deadline or (date.today() + timedelta(days=30))
        period = period or filing_deadline.strftime("%b %Y")

        values = {
            "name": name or f"Test BIR Schedule {unique_id}",
            "period_covered": period,
            "filing_deadline": filing_deadline,
            "prep_deadline": filing_deadline - timedelta(days=4),
            "review_deadline": filing_deadline - timedelta(days=2),
            "approval_deadline": filing_deadline - timedelta(days=1),
            **kwargs,
        }

        if supervisor:
            values["supervisor_id"] = supervisor.id
        if reviewer:
            values["reviewer_id"] = reviewer.id
        if approver:
            values["approver_id"] = approver.id

        return self.env["ipai.finance.bir_schedule"].create(values)

    # -------------------------------------------------------------------------
    # Equipment Factories
    # -------------------------------------------------------------------------

    @api.model
    def create_equipment_asset(
        self,
        name=None,
        condition="good",
        status="available",
        **kwargs,
    ):
        """
        Create a test equipment asset.

        Args:
            name: Asset name (auto-generated if not provided)
            condition: Asset condition (new, good, used, damaged)
            status: Asset status (available, reserved, checked_out, maintenance)
            **kwargs: Additional fields to set

        Returns:
            ipai.equipment.asset record (if module installed)
        """
        if "ipai.equipment.asset" not in self.env:
            return None

        unique_id = str(uuid.uuid4())[:8]
        values = {
            "name": name or f"Test Asset {unique_id}",
            "condition": condition,
            "status": status,
            **kwargs,
        }

        return self.env["ipai.equipment.asset"].create(values)

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    @api.model
    def get_admin_user(self):
        """Get the admin user for testing."""
        return self.env.ref("base.user_admin")

    @api.model
    def get_demo_user(self):
        """Get the demo user for testing (if available)."""
        try:
            return self.env.ref("base.user_demo")
        except ValueError:
            return self.create_user(name="Demo User", login="demo")
