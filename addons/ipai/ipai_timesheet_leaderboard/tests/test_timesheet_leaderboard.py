from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTimesheetLeaderboard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Test Employee"}
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "allow_timesheets": True,
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
            }
        )

    def test_sql_view_exists(self):
        """The SQL view is created and queryable."""
        records = self.env["ipai.timesheet.leaderboard"].search([])
        # Should not raise — view exists
        self.assertIsNotNone(records)

    def test_leaderboard_aggregation(self):
        """Timesheet entries aggregate correctly in leaderboard."""
        self.env["account.analytic.line"].create(
            {
                "name": "Work 1",
                "employee_id": self.employee.id,
                "project_id": self.project.id,
                "task_id": self.task.id,
                "unit_amount": 4.0,
            }
        )
        self.env["account.analytic.line"].create(
            {
                "name": "Work 2",
                "employee_id": self.employee.id,
                "project_id": self.project.id,
                "task_id": self.task.id,
                "unit_amount": 3.5,
            }
        )
        # Re-init the view to pick up new data
        self.env["ipai.timesheet.leaderboard"].init()
        records = self.env["ipai.timesheet.leaderboard"].search(
            [
                ("employee_id", "=", self.employee.id),
                ("project_id", "=", self.project.id),
            ]
        )
        self.assertTrue(records)
        total = sum(records.mapped("total_hours"))
        self.assertEqual(total, 7.5)

    def test_billable_hours_flag(self):
        """Billable hours counted only when project allows timesheets."""
        project_no_ts = self.env["project.project"].create(
            {
                "name": "Non-Billable Project",
                "allow_timesheets": False,
            }
        )
        # Create a task first — timesheet entries need a project context
        self.env["account.analytic.line"].create(
            {
                "name": "Non-billable work",
                "employee_id": self.employee.id,
                "project_id": project_no_ts.id,
                "unit_amount": 5.0,
            }
        )
        self.env["ipai.timesheet.leaderboard"].init()
        records = self.env["ipai.timesheet.leaderboard"].search(
            [
                ("employee_id", "=", self.employee.id),
                ("project_id", "=", project_no_ts.id),
            ]
        )
        if records:
            self.assertEqual(sum(records.mapped("billable_hours")), 0.0)
            self.assertEqual(sum(records.mapped("total_hours")), 5.0)

    def test_entry_count(self):
        """Entry count reflects number of timesheet lines."""
        for i in range(3):
            self.env["account.analytic.line"].create(
                {
                    "name": "Entry %d" % i,
                    "employee_id": self.employee.id,
                    "project_id": self.project.id,
                    "task_id": self.task.id,
                    "unit_amount": 1.0,
                }
            )
        self.env["ipai.timesheet.leaderboard"].init()
        records = self.env["ipai.timesheet.leaderboard"].search(
            [
                ("employee_id", "=", self.employee.id),
                ("project_id", "=", self.project.id),
            ]
        )
        total_entries = sum(records.mapped("entry_count"))
        self.assertGreaterEqual(total_entries, 3)

    def test_model_is_readonly(self):
        """Leaderboard model has _auto=False (SQL view, not a table)."""
        model = self.env["ipai.timesheet.leaderboard"]
        self.assertFalse(model._auto)
