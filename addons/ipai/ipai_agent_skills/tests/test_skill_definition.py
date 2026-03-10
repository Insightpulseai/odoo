# -*- coding: utf-8 -*-
import json

from odoo.tests.common import TransactionCase


class TestSkillDefinition(TransactionCase):
    """Test ipai.skill.definition model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["ipai.skill.category"].create(
            {
                "name": "Test Category",
                "code": "test",
                "sequence": 99,
            }
        )
        cls.skill = cls.env["ipai.skill.definition"].create(
            {
                "name": "Test Skill",
                "key": "test.skill",
                "category_id": cls.category.id,
                "description": "A test skill",
                "intent_ids": json.dumps(["test intent", "another test intent"]),
                "tool_ids": json.dumps(
                    [
                        {
                            "key": "test.tool",
                            "name": "Test Tool",
                            "target_model": "test.model",
                            "target_method": "test_method",
                        }
                    ]
                ),
                "workflow": json.dumps(["test.tool"]),
            }
        )

    def test_skill_creation(self):
        """Skill is created with correct fields."""
        self.assertEqual(self.skill.name, "Test Skill")
        self.assertEqual(self.skill.key, "test.skill")
        self.assertEqual(self.skill.category_id, self.category)

    def test_get_intents_list(self):
        """Intents JSON is parsed correctly."""
        intents = self.skill.get_intents_list()
        self.assertEqual(len(intents), 2)
        self.assertIn("test intent", intents)

    def test_get_tools_list(self):
        """Tools JSON is parsed correctly."""
        tools = self.skill.get_tools_list()
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["key"], "test.tool")

    def test_get_workflow_list(self):
        """Workflow JSON is parsed correctly."""
        workflow = self.skill.get_workflow_list()
        self.assertEqual(workflow, ["test.tool"])

    def test_invalid_json_returns_empty(self):
        """Invalid JSON fields return empty list."""
        self.skill.write({"intent_ids": "not valid json"})
        self.assertEqual(self.skill.get_intents_list(), [])

    def test_key_uniqueness(self):
        """Duplicate skill keys are rejected."""
        with self.assertRaises(Exception):
            self.env["ipai.skill.definition"].create(
                {
                    "name": "Duplicate Skill",
                    "key": "test.skill",
                }
            )

    def test_category_skill_count(self):
        """Category computes skill count correctly."""
        self.assertEqual(self.category.skill_count, 1)

    def test_execution_lifecycle(self):
        """Execution state transitions work correctly."""
        execution = self.env["ipai.skill.execution"].create(
            {
                "skill_id": self.skill.id,
                "input_data": json.dumps({"test": True}),
            }
        )
        self.assertEqual(execution.state, "queued")

        execution.action_start()
        self.assertEqual(execution.state, "running")
        self.assertTrue(execution.started_at)

        execution.action_complete({"result": "ok"})
        self.assertEqual(execution.state, "completed")
        self.assertTrue(execution.completed_at)
        self.assertIn("ok", execution.output_data)

    def test_execution_failure(self):
        """Execution failure records error message."""
        execution = self.env["ipai.skill.execution"].create({"skill_id": self.skill.id})
        execution.action_start()
        execution.action_fail("Something went wrong")
        self.assertEqual(execution.state, "failed")
        self.assertEqual(execution.error_message, "Something went wrong")
