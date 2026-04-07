from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged("post_install", "-at_install")
class TestClosingTaskList(TransactionCase):
    """Test closing template → task list → task lifecycle."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")

        # Create a template with 3 lines (MEC-010, MEC-020, MEC-030)
        cls.template = cls.env["closing.template"].create({
            "name": "Test Month-End",
            "code": "MEC",
            "closing_type": "month_end",
            "company_id": cls.company.id,
        })
        cls.line1 = cls.env["closing.template.line"].create({
            "template_id": cls.template.id,
            "name": "Reconcile bank",
            "code": "MEC-010",
            "sequence": 10,
            "task_type": "manual",
            "stage": "preparation",
            "deadline_reference": "period_end",
            "deadline_offset_days": -3,
        })
        cls.line2 = cls.env["closing.template.line"].create({
            "template_id": cls.template.id,
            "name": "Review receivables",
            "code": "MEC-020",
            "sequence": 20,
            "task_type": "manual",
            "stage": "preparation",
            "deadline_reference": "period_end",
            "deadline_offset_days": -3,
        })
        cls.line3 = cls.env["closing.template.line"].create({
            "template_id": cls.template.id,
            "name": "Final approval",
            "code": "MEC-030",
            "sequence": 30,
            "task_type": "approval",
            "stage": "approval",
            "deadline_reference": "period_end",
            "deadline_offset_days": 1,
            "dependency_codes": "MEC-010,MEC-020",
        })

    def test_template_line_count(self):
        self.assertEqual(self.template.line_count, 3)

    def test_generate_tasks(self):
        task_list = self.env["closing.task.list"].create({
            "name": "March 2026 Close",
            "template_id": self.template.id,
            "period_start": "2026-03-01",
            "period_end": "2026-03-31",
            "company_id": self.company.id,
        })
        self.assertEqual(task_list.state, "draft")

        task_list.action_generate_tasks()
        self.assertEqual(task_list.state, "in_progress")
        self.assertEqual(len(task_list.task_ids), 3)

        # Check deadlines computed correctly
        task_010 = task_list.task_ids.filtered(lambda t: t.code == "MEC-010")
        self.assertEqual(str(task_010.planned_date), "2026-03-28")  # March 31 - 3

        task_030 = task_list.task_ids.filtered(lambda t: t.code == "MEC-030")
        self.assertEqual(str(task_030.planned_date), "2026-04-01")  # March 31 + 1

    def test_dependency_blocks_start(self):
        task_list = self.env["closing.task.list"].create({
            "name": "Dep Test",
            "template_id": self.template.id,
            "period_start": "2026-03-01",
            "period_end": "2026-03-31",
            "company_id": self.company.id,
        })
        task_list.action_generate_tasks()

        task_030 = task_list.task_ids.filtered(lambda t: t.code == "MEC-030")
        self.assertFalse(task_030.can_start)

        with self.assertRaises(UserError):
            task_030.action_start()

    def test_auto_close_cascade(self):
        """SAP cascade: all tasks completed → task list auto-closes."""
        task_list = self.env["closing.task.list"].create({
            "name": "Cascade Test",
            "template_id": self.template.id,
            "period_start": "2026-03-01",
            "period_end": "2026-03-31",
            "company_id": self.company.id,
        })
        task_list.action_generate_tasks()

        for task in task_list.task_ids.sorted("sequence"):
            task.action_start()
            task.action_complete()

        self.assertEqual(task_list.state, "closed")

    def test_cannot_close_with_open_tasks(self):
        task_list = self.env["closing.task.list"].create({
            "name": "Block Test",
            "template_id": self.template.id,
            "period_start": "2026-03-01",
            "period_end": "2026-03-31",
            "company_id": self.company.id,
        })
        task_list.action_generate_tasks()

        with self.assertRaises(UserError):
            task_list.action_close()
