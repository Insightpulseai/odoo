# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIpaiAiAgent(TransactionCase):
    """Test cases for IPAI AI Agent Builder."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Agent = cls.env["ipai.ai.agent"]
        cls.Topic = cls.env["ipai.ai.topic"]
        cls.Tool = cls.env["ipai.ai.tool"]

    def test_create_agent(self):
        """Test creating an AI agent."""
        agent = self.Agent.create({
            "name": "Test Agent",
            "system_prompt": "You are a helpful assistant.",
            "provider": "openai",
            "model": "gpt-4o",
        })
        self.assertTrue(agent.id)
        self.assertEqual(agent.name, "Test Agent")
        self.assertEqual(agent.provider, "openai")
        self.assertTrue(agent.active)

    def test_create_topic(self):
        """Test creating a topic for an agent."""
        agent = self.Agent.create({
            "name": "Test Agent",
            "provider": "openai",
        })
        topic = self.Topic.create({
            "name": "Test Topic",
            "agent_id": agent.id,
            "instructions": "Help with testing.",
        })
        self.assertTrue(topic.id)
        self.assertEqual(topic.agent_id.id, agent.id)
        self.assertIn(topic, agent.topic_ids)

    def test_create_tool(self):
        """Test creating an AI tool."""
        tool = self.Tool.create({
            "key": "test_tool",
            "name": "Test Tool",
            "description": "A test tool",
            "python_entrypoint": "odoo.addons.ipai_ai_tools.tools.test:test_func",
        })
        self.assertTrue(tool.id)
        self.assertEqual(tool.key, "test_tool")

    def test_tool_key_unique(self):
        """Test that tool keys must be unique."""
        self.Tool.create({
            "key": "unique_tool",
            "name": "Tool 1",
            "python_entrypoint": "module:func1",
        })
        with self.assertRaises(Exception):
            self.Tool.create({
                "key": "unique_tool",
                "name": "Tool 2",
                "python_entrypoint": "module:func2",
            })

    def test_tool_entrypoint_validation(self):
        """Test that tool entrypoint format is validated."""
        with self.assertRaises(Exception):
            self.Tool.create({
                "key": "bad_tool",
                "name": "Bad Tool",
                "python_entrypoint": "invalid_format_without_colon",
            })

    def test_get_all_tools(self):
        """Test getting all tools from an agent's topics."""
        agent = self.Agent.create({
            "name": "Test Agent",
            "provider": "openai",
        })
        tool1 = self.Tool.create({
            "key": "tool1",
            "name": "Tool 1",
            "python_entrypoint": "module:func1",
        })
        tool2 = self.Tool.create({
            "key": "tool2",
            "name": "Tool 2",
            "python_entrypoint": "module:func2",
        })
        self.Topic.create({
            "name": "Topic 1",
            "agent_id": agent.id,
            "tool_ids": [(6, 0, [tool1.id])],
        })
        self.Topic.create({
            "name": "Topic 2",
            "agent_id": agent.id,
            "tool_ids": [(6, 0, [tool2.id])],
        })
        all_tools = agent.get_all_tools()
        self.assertEqual(len(all_tools), 2)
        self.assertIn(tool1, all_tools)
        self.assertIn(tool2, all_tools)

    def test_tool_permission_no_groups(self):
        """Test that tools without groups allow all users."""
        tool = self.Tool.create({
            "key": "open_tool",
            "name": "Open Tool",
            "python_entrypoint": "module:func",
        })
        self.assertTrue(tool.check_permission())

    def test_tool_llm_definition(self):
        """Test generating LLM-compatible tool definition."""
        tool = self.Tool.create({
            "key": "test_tool",
            "name": "Test Tool",
            "description": "A test tool for testing",
            "python_entrypoint": "module:func",
            "parameters_schema": '{"type": "object", "properties": {"name": {"type": "string"}}}',
        })
        definition = tool.get_llm_definition()
        self.assertEqual(definition["type"], "function")
        self.assertEqual(definition["function"]["name"], "test_tool")
        self.assertEqual(definition["function"]["description"], "A test tool for testing")
        self.assertIn("parameters", definition["function"])

    def test_run_creation(self):
        """Test creating a run record."""
        agent = self.Agent.create({
            "name": "Test Agent",
            "provider": "openai",
        })
        run = self.env["ipai.ai.run"].create({
            "agent_id": agent.id,
            "input": "Hello",
        })
        self.assertTrue(run.id)
        self.assertEqual(run.agent_id.id, agent.id)
        self.assertEqual(run.user_id.id, self.env.uid)

    def test_run_log_event(self):
        """Test logging events for a run."""
        agent = self.Agent.create({
            "name": "Test Agent",
            "provider": "openai",
        })
        run = self.env["ipai.ai.run"].create({
            "agent_id": agent.id,
            "input": "Hello",
        })
        run.log_event("start", {"message": "Hello"})
        run.log_event("end", {"status": "success"})
        self.assertEqual(len(run.event_ids), 2)
        self.assertEqual(run.event_ids[0].event_type, "start")
        self.assertEqual(run.event_ids[1].event_type, "end")
