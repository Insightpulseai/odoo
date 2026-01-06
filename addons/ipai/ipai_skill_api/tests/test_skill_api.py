# -*- coding: utf-8 -*-
"""Unit tests for IPAI Skill API."""

import json
from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSkillAPI(TransactionCase):
    """Test cases for Skill API controller."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test skill
        cls.test_skill = cls.env["ipai.agent.skill"].create({
            "name": "Test Skill",
            "key": "test.skill.api",
            "version": "1.0.0",
            "description": "A test skill for API testing",
            "intents": "test something\nvalidate api",
            "guardrails": "do not fail\nbe deterministic",
            "workflow_json": '["tool.one", "tool.two"]',
            "is_active": True,
        })

        # Create test tool
        cls.test_tool = cls.env["ipai.agent.tool"].create({
            "name": "Test Tool One",
            "key": "tool.one",
            "description": "First test tool",
            "target_model": "res.partner",
            "target_method": "name_get",
            "is_active": True,
        })

        cls.test_skill.tool_ids = [(4, cls.test_tool.id)]

    def test_skill_to_dict_basic(self):
        """Test basic skill serialization."""
        from odoo.addons.ipai_skill_api.controllers.main import SkillAPIController

        controller = SkillAPIController()
        result = controller._skill_to_dict(self.test_skill)

        self.assertEqual(result["key"], "test.skill.api")
        self.assertEqual(result["name"], "Test Skill")
        self.assertEqual(result["version"], "1.0.0")
        self.assertTrue(result["is_active"])

    def test_skill_to_dict_full(self):
        """Test full skill serialization with tools."""
        from odoo.addons.ipai_skill_api.controllers.main import SkillAPIController

        controller = SkillAPIController()
        result = controller._skill_to_dict(self.test_skill, full=True)

        self.assertIn("intents", result)
        self.assertIn("guardrails", result)
        self.assertIn("workflow", result)
        self.assertIn("tools", result)

        self.assertEqual(result["intents"], ["test something", "validate api"])
        self.assertEqual(result["guardrails"], ["do not fail", "be deterministic"])
        self.assertEqual(result["workflow"], ["tool.one", "tool.two"])
        self.assertEqual(len(result["tools"]), 1)
        self.assertEqual(result["tools"][0]["key"], "tool.one")

    def test_create_run_via_model(self):
        """Test run creation via model (simulating API)."""
        Run = self.env["ipai.agent.run"]

        run = Run.create({
            "skill_id": self.test_skill.id,
            "input_text": "Test input",
            "input_json": json.dumps({"test": True}),
        })

        self.assertEqual(run.state, "draft")
        self.assertEqual(run.skill_key, "test.skill.api")
        self.assertEqual(run.input_text, "Test input")

        # Verify input_json parsing
        input_dict = run.get_input_dict()
        self.assertTrue(input_dict.get("test"))

    def test_run_state_transitions(self):
        """Test run state machine."""
        Run = self.env["ipai.agent.run"]

        run = Run.create({
            "skill_id": self.test_skill.id,
            "input_text": "State test",
        })

        self.assertEqual(run.state, "draft")

        # Can't reset a draft run
        run.action_reset_to_draft()
        self.assertEqual(run.state, "draft")

    def test_skill_intents_parsing(self):
        """Test intents multiline parsing."""
        intents = self.test_skill.get_intents_list()
        self.assertEqual(len(intents), 2)
        self.assertEqual(intents[0], "test something")
        self.assertEqual(intents[1], "validate api")

    def test_skill_guardrails_parsing(self):
        """Test guardrails multiline parsing."""
        guardrails = self.test_skill.get_guardrails_list()
        self.assertEqual(len(guardrails), 2)
        self.assertEqual(guardrails[0], "do not fail")
        self.assertEqual(guardrails[1], "be deterministic")

    def test_skill_workflow_parsing(self):
        """Test workflow JSON parsing."""
        workflow = self.test_skill.get_workflow_tools()
        self.assertEqual(len(workflow), 2)
        self.assertEqual(workflow[0], "tool.one")
        self.assertEqual(workflow[1], "tool.two")

    def test_inactive_skill_filtering(self):
        """Test that inactive skills are not returned."""
        Skill = self.env["ipai.agent.skill"]

        # Create inactive skill
        inactive_skill = Skill.create({
            "name": "Inactive Skill",
            "key": "test.skill.inactive",
            "is_active": False,
        })

        # Search should not return inactive
        active_skills = Skill.search([("is_active", "=", True)])
        self.assertIn(self.test_skill, active_skills)
        self.assertNotIn(inactive_skill, active_skills)
