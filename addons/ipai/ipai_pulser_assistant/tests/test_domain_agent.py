# -*- coding: utf-8 -*-
"""
Tests for pulser.domain.agent — domain agent routing contract.

Validates: agent creation, tool binding association, supported intent
linkage, domain key constraints.
"""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("pulser", "joule", "post_install", "-at_install")
class TestPulserDomainAgent(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Agent = self.env["pulser.domain.agent"]
        self.Intent = self.env["pulser.intent"]
        self.ActionClass = self.env["pulser.action.class"]
        self.ToolBinding = self.env["pulser.tool.binding"]

        # Shared fixtures
        self.advisory_class = self.ActionClass.create({
            "name": "Agent Test Advisory",
            "class_type": "advisory",
        })
        self.approval_class = self.ActionClass.create({
            "name": "Agent Test Approval",
            "class_type": "approval_gated",
        })
        self.info_intent = self.Intent.create({
            "name": "Agent Test: Query Status",
            "intent_type": "informational",
        })
        self.txn_intent = self.Intent.create({
            "name": "Agent Test: Submit Report",
            "intent_type": "transactional",
        })

    # ---- Creation ----

    def test_agent_creation(self):
        agent = self.Agent.create({
            "name": "Expense Agent",
            "domain": "expense",
            "description": "Handles expense submission and liquidation",
        })
        self.assertEqual(agent.name, "Expense Agent")
        self.assertEqual(agent.domain, "expense")
        self.assertTrue(agent.is_active)

    def test_project_agent_creation(self):
        agent = self.Agent.create({
            "name": "Project Agent",
            "domain": "project",
        })
        self.assertEqual(agent.domain, "project")

    # ---- Domain key constraints ----

    def test_domain_key_unique(self):
        self.Agent.create({"name": "Expense A", "domain": "expense_unique_test"})
        with self.assertRaises(Exception):
            self.Agent.create({"name": "Expense B", "domain": "expense_unique_test"})

    def test_domain_key_no_spaces(self):
        with self.assertRaises(ValidationError):
            self.Agent.create({"name": "Bad Agent", "domain": "expense report"})

    def test_domain_key_blank_raises(self):
        with self.assertRaises(ValidationError):
            self.Agent.create({"name": "No Domain", "domain": "   "})

    # ---- Tool bindings ----

    def test_agent_tool_binding_creation(self):
        agent = self.Agent.create({"name": "Binding Agent", "domain": "binding_test"})
        tool = self.ToolBinding.create({
            "agent_id": agent.id,
            "name": "get_expense_status",
            "model_name": "hr.expense",
            "method_name": "search_read",
            "action_class_id": self.advisory_class.id,
            "is_read_only": True,
        })
        self.assertEqual(tool.agent_id, agent)
        self.assertEqual(agent.tool_count, 1)

    def test_agent_multiple_tool_bindings(self):
        agent = self.Agent.create({"name": "Multi-Tool Agent", "domain": "multi_tool_test"})
        for i in range(3):
            self.ToolBinding.create({
                "agent_id": agent.id,
                "name": f"tool_{i}",
                "model_name": "hr.expense",
                "method_name": "search_read",
                "action_class_id": self.advisory_class.id,
                "is_read_only": True,
            })
        self.assertEqual(agent.tool_count, 3)

    def test_tool_binding_name_unique_per_agent(self):
        agent = self.Agent.create({"name": "Unique Tool Agent", "domain": "unique_tool_test"})
        self.ToolBinding.create({
            "agent_id": agent.id,
            "name": "duplicate_tool",
            "model_name": "hr.expense",
            "method_name": "search_read",
            "action_class_id": self.advisory_class.id,
        })
        with self.assertRaises(Exception):
            self.ToolBinding.create({
                "agent_id": agent.id,
                "name": "duplicate_tool",
                "model_name": "project.project",
                "method_name": "search_read",
                "action_class_id": self.advisory_class.id,
            })

    def test_read_only_tool_with_approval_class_raises(self):
        agent = self.Agent.create({"name": "Safety Agent", "domain": "safety_test"})
        with self.assertRaises(ValidationError):
            self.ToolBinding.create({
                "agent_id": agent.id,
                "name": "bad_read_only",
                "model_name": "hr.expense",
                "method_name": "search_read",
                "action_class_id": self.approval_class.id,
                "is_read_only": True,
            })

    # ---- Intent support ----

    def test_agent_intent_support(self):
        agent = self.Agent.create({
            "name": "Intent Agent",
            "domain": "intent_test",
            "supported_intent_ids": [(4, self.info_intent.id), (4, self.txn_intent.id)],
        })
        self.assertIn(self.info_intent, agent.supported_intent_ids)
        self.assertIn(self.txn_intent, agent.supported_intent_ids)

    def test_agent_no_intents(self):
        """Agent with no intents configured is valid — intents are optional."""
        agent = self.Agent.create({"name": "Bare Agent", "domain": "bare_agent_test"})
        self.assertEqual(len(agent.supported_intent_ids), 0)

    # ---- Deactivation ----

    def test_agent_deactivation(self):
        agent = self.Agent.create({"name": "Deactivate Me", "domain": "deactivate_test"})
        agent.is_active = False
        self.assertFalse(agent.is_active)
