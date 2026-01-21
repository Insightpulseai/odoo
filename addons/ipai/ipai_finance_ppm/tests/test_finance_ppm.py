# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024 InsightPulseAI
"""
Test cases for IPAI Finance PPM module.

Tests cover:
- Finance Logframe lifecycle (creation, levels, task linking)
- BIR Schedule management (status transitions, deadline tracking)
- Cron job for task synchronization
- Completion percentage calculations
"""
from datetime import date, timedelta
from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "ipai_finance_ppm")
class TestFinanceLogframe(TransactionCase):
    """Test Finance Logframe model functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test data for logframe tests."""
        super().setUpClass()
        cls.Logframe = cls.env["ipai.finance.logframe"]

    def test_01_logframe_creation(self):
        """Test logframe is created with required fields."""
        logframe = self.Logframe.create(
            {
                "level": "goal",
                "name": "Test Goal",
                "code": "TG1",
            }
        )

        self.assertEqual(logframe.level, "goal")
        self.assertEqual(logframe.name, "Test Goal")
        self.assertEqual(logframe.code, "TG1")

    def test_02_logframe_levels(self):
        """Test all logframe levels can be created."""
        levels = [
            "goal",
            "outcome",
            "im1",
            "im2",
            "output",
            "activity_im1",
            "activity_im2",
        ]

        for level in levels:
            logframe = self.Logframe.create(
                {
                    "level": level,
                    "name": f"Test {level.title()}",
                }
            )
            self.assertEqual(
                logframe.level, level, f"Level {level} should be created correctly"
            )

    def test_03_logframe_task_count_computed(self):
        """Test task count is computed correctly."""
        logframe = self.Logframe.create(
            {
                "level": "output",
                "name": "Test Output",
            }
        )

        # Initially no tasks
        self.assertEqual(logframe.task_count, 0)

        # Create tasks linked to logframe
        project = self.env["project.project"].create({"name": "Test Project"})

        for i in range(3):
            self.env["project.task"].create(
                {
                    "name": f"Task {i + 1}",
                    "project_id": project.id,
                    "finance_logframe_id": logframe.id,
                }
            )

        # Refresh and check count
        logframe.invalidate_recordset()
        self.assertEqual(logframe.task_count, 3)

    def test_04_logframe_optional_fields(self):
        """Test logframe optional fields."""
        logframe = self.Logframe.create(
            {
                "level": "im1",
                "name": "Immediate Objective 1",
                "code": "IM1",
                "indicators": "Number of compliance filings",
                "means_of_verification": "BIR receipts and confirmations",
                "assumptions": "Stable tax regulations",
            }
        )

        self.assertEqual(logframe.indicators, "Number of compliance filings")
        self.assertEqual(
            logframe.means_of_verification, "BIR receipts and confirmations"
        )
        self.assertEqual(logframe.assumptions, "Stable tax regulations")


@tagged("post_install", "-at_install", "ipai_finance_ppm")
class TestFinanceBIRSchedule(TransactionCase):
    """Test BIR Schedule model functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test data for BIR schedule tests."""
        super().setUpClass()
        cls.BIRSchedule = cls.env["ipai.finance.bir_schedule"]
        cls.admin = cls.env.ref("base.user_admin")

    def test_01_schedule_creation(self):
        """Test BIR schedule is created with correct defaults."""
        schedule = self.BIRSchedule.create(
            {
                "name": "1601-C (Compensation) – Jan 2026",
                "period_covered": "Jan 2026",
                "filing_deadline": date(2026, 1, 15),
            }
        )

        self.assertEqual(schedule.name, "1601-C (Compensation) – Jan 2026")
        self.assertEqual(schedule.status, "not_started")
        self.assertEqual(schedule.completion_pct, 0.0)

    def test_02_schedule_status_transitions(self):
        """Test status can be updated to all valid states."""
        statuses = ["not_started", "in_progress", "submitted", "filed", "late"]

        for status in statuses:
            schedule = self.BIRSchedule.create(
                {
                    "name": f"Test Schedule {status}",
                    "filing_deadline": date.today() + timedelta(days=30),
                    "status": status,
                }
            )
            self.assertEqual(
                schedule.status, status, f"Status {status} should be set correctly"
            )

    def test_03_schedule_with_deadlines(self):
        """Test schedule with all deadline fields."""
        filing = date(2026, 2, 15)
        schedule = self.BIRSchedule.create(
            {
                "name": "1604-E – Feb 2026",
                "period_covered": "Feb 2026",
                "filing_deadline": filing,
                "prep_deadline": filing - timedelta(days=4),
                "review_deadline": filing - timedelta(days=2),
                "approval_deadline": filing - timedelta(days=1),
            }
        )

        self.assertEqual(schedule.filing_deadline, date(2026, 2, 15))
        self.assertEqual(schedule.prep_deadline, date(2026, 2, 11))
        self.assertEqual(schedule.review_deadline, date(2026, 2, 13))
        self.assertEqual(schedule.approval_deadline, date(2026, 2, 14))

    def test_04_schedule_with_assignees(self):
        """Test schedule with assigned users."""
        schedule = self.BIRSchedule.create(
            {
                "name": "Test Assigned Schedule",
                "filing_deadline": date.today() + timedelta(days=30),
                "supervisor_id": self.admin.id,
                "reviewer_id": self.admin.id,
                "approver_id": self.admin.id,
            }
        )

        self.assertEqual(schedule.supervisor_id, self.admin)
        self.assertEqual(schedule.reviewer_id, self.admin)
        self.assertEqual(schedule.approver_id, self.admin)

    def test_05_schedule_late_detection(self):
        """Test that past-due schedules can be marked as late."""
        schedule = self.BIRSchedule.create(
            {
                "name": "Past Due Schedule",
                "filing_deadline": date.today() - timedelta(days=5),
                "status": "not_started",
            }
        )

        # Manually set to late (normally done by cron)
        schedule.status = "late"
        self.assertEqual(schedule.status, "late")

    def test_06_schedule_completion_percentage(self):
        """Test completion percentage tracking."""
        schedule = self.BIRSchedule.create(
            {
                "name": "Progress Test Schedule",
                "filing_deadline": date.today() + timedelta(days=30),
            }
        )

        # Update completion
        schedule.completion_pct = 33.33
        self.assertAlmostEqual(schedule.completion_pct, 33.33, places=2)

        schedule.completion_pct = 100.0
        self.assertEqual(schedule.completion_pct, 100.0)

    def test_07_schedule_logframe_link(self):
        """Test schedule can be linked to logframe."""
        logframe = self.env["ipai.finance.logframe"].create(
            {
                "level": "im2",
                "name": "Tax Filing Compliance",
            }
        )

        schedule = self.BIRSchedule.create(
            {
                "name": "Linked Schedule",
                "filing_deadline": date.today() + timedelta(days=30),
                "logframe_id": logframe.id,
            }
        )

        self.assertEqual(schedule.logframe_id, logframe)
        self.assertIn(schedule, logframe.bir_schedule_ids)


@tagged("post_install", "-at_install", "ipai_finance_ppm", "cron")
class TestBIRCronSync(TransactionCase):
    """Test BIR task synchronization cron job."""

    @classmethod
    def setUpClass(cls):
        """Set up test data for cron tests."""
        super().setUpClass()
        cls.BIRSchedule = cls.env["ipai.finance.bir_schedule"]
        cls.Project = cls.env["project.project"]
        cls.Task = cls.env["project.task"]
        cls.admin = cls.env.ref("base.user_admin")

    def test_01_cron_creates_project_if_missing(self):
        """Test cron creates the finance project if it doesn't exist."""
        # Delete existing project if any
        existing = self.Project.search(
            [("name", "=", "TBWA Finance – Month-End & BIR")]
        )
        existing.unlink()

        # Create a schedule
        schedule = self.BIRSchedule.create(
            {
                "name": "Cron Test Schedule",
                "filing_deadline": date.today() + timedelta(days=30),
                "prep_deadline": date.today() + timedelta(days=26),
                "review_deadline": date.today() + timedelta(days=28),
                "approval_deadline": date.today() + timedelta(days=29),
                "supervisor_id": self.admin.id,
            }
        )

        # Run cron
        self.BIRSchedule._cron_sync_bir_tasks()

        # Verify project was created
        project = self.Project.search(
            [("name", "=", "TBWA Finance – Month-End & BIR")], limit=1
        )
        self.assertTrue(project, "Finance project should be created")

    def test_02_cron_creates_tasks(self):
        """Test cron creates 3 tasks per schedule."""
        # Ensure project exists
        project = self.Project.search(
            [("name", "=", "TBWA Finance – Month-End & BIR")], limit=1
        )
        if not project:
            project = self.Project.create({"name": "TBWA Finance – Month-End & BIR"})

        # Create schedule with assignees
        schedule = self.BIRSchedule.create(
            {
                "name": "Task Creation Test",
                "filing_deadline": date.today() + timedelta(days=30),
                "prep_deadline": date.today() + timedelta(days=26),
                "review_deadline": date.today() + timedelta(days=28),
                "approval_deadline": date.today() + timedelta(days=29),
                "supervisor_id": self.admin.id,
                "reviewer_id": self.admin.id,
                "approver_id": self.admin.id,
            }
        )

        # Run cron
        self.BIRSchedule._cron_sync_bir_tasks()

        # Refresh schedule
        schedule.invalidate_recordset()

        # Verify tasks were created
        self.assertTrue(schedule.prep_task_id, "Preparation task should be created")
        self.assertTrue(schedule.review_task_id, "Review task should be created")
        self.assertTrue(schedule.approval_task_id, "Approval task should be created")

        # Verify task names
        self.assertIn("Preparation", schedule.prep_task_id.name)
        self.assertIn("Review", schedule.review_task_id.name)
        self.assertIn("Approval", schedule.approval_task_id.name)

    def test_03_cron_skips_filed_schedules(self):
        """Test cron skips schedules that are already filed."""
        schedule = self.BIRSchedule.create(
            {
                "name": "Filed Schedule",
                "filing_deadline": date.today() - timedelta(days=5),
                "status": "filed",
            }
        )

        # Run cron
        self.BIRSchedule._cron_sync_bir_tasks()

        # Verify no tasks were created
        schedule.invalidate_recordset()
        self.assertFalse(
            schedule.prep_task_id, "No tasks should be created for filed schedules"
        )

    def test_04_cron_updates_existing_tasks(self):
        """Test cron updates existing tasks instead of creating duplicates."""
        project = self.Project.search(
            [("name", "=", "TBWA Finance – Month-End & BIR")], limit=1
        )
        if not project:
            project = self.Project.create({"name": "TBWA Finance – Month-End & BIR"})

        # Create schedule with initial deadline
        original_deadline = date.today() + timedelta(days=30)
        schedule = self.BIRSchedule.create(
            {
                "name": "Update Test",
                "filing_deadline": original_deadline,
                "prep_deadline": original_deadline - timedelta(days=4),
                "supervisor_id": self.admin.id,
            }
        )

        # First run - creates tasks
        self.BIRSchedule._cron_sync_bir_tasks()
        schedule.invalidate_recordset()
        first_task_id = schedule.prep_task_id.id

        # Update deadline
        new_deadline = original_deadline + timedelta(days=7)
        schedule.prep_deadline = new_deadline - timedelta(days=4)

        # Second run - should update, not recreate
        self.BIRSchedule._cron_sync_bir_tasks()
        schedule.invalidate_recordset()

        # Verify same task was updated
        self.assertEqual(schedule.prep_task_id.id, first_task_id)
        self.assertEqual(
            schedule.prep_task_id.date_deadline, new_deadline - timedelta(days=4)
        )
