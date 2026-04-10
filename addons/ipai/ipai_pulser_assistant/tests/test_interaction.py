# -*- coding: utf-8 -*-
"""
Tests for pulser.interaction — interaction trace.

Validates: interaction creation, session tracking, feedback lifecycle,
action log linkage, and session_id constraint.
"""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("pulser", "joule", "post_install", "-at_install")
class TestPulserInteraction(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Interaction = self.env["pulser.interaction"]
        self.ActionLog = self.env["pulser.action.log"]
        self.Agent = self.env["pulser.domain.agent"]

        self.expense_agent = self.Agent.create({
            "name": "Interaction Test Expense Agent",
            "domain": "interaction_test_expense",
        })

    def _make_interaction(self, session_id="test-session-001", **kwargs):
        defaults = {
            "session_id": session_id,
            "user_id": self.env.user.id,
            "query": "What is the status of my expense reports?",
            "intent_type": "informational",
        }
        defaults.update(kwargs)
        return self.Interaction.create(defaults)

    # ---- Creation ----

    def test_interaction_creation(self):
        interaction = self._make_interaction()
        self.assertEqual(interaction.session_id, "test-session-001")
        self.assertTrue(interaction.timestamp)
        self.assertEqual(interaction.user_id, self.env.user)

    def test_interaction_with_response(self):
        interaction = self._make_interaction(
            response="You have 3 pending expense reports.",
        )
        self.assertIn("3", interaction.response)

    def test_interaction_default_feedback_none(self):
        interaction = self._make_interaction()
        self.assertEqual(interaction.feedback, "none")

    # ---- Session tracking ----

    def test_interaction_session_tracking_same_session(self):
        """Two interactions with the same session_id is allowed (multi-turn)."""
        i1 = self._make_interaction(session_id="shared-session-001")
        i2 = self._make_interaction(
            session_id="shared-session-001",
            query="What about invoices?",
        )
        self.assertEqual(i1.session_id, i2.session_id)

    def test_interaction_different_sessions(self):
        i1 = self._make_interaction(session_id="session-A")
        i2 = self._make_interaction(session_id="session-B")
        self.assertNotEqual(i1.session_id, i2.session_id)

    def test_interaction_session_id_blank_raises(self):
        with self.assertRaises(ValidationError):
            self._make_interaction(session_id="   ")

    def test_interaction_session_id_empty_raises(self):
        with self.assertRaises(ValidationError):
            self._make_interaction(session_id="")

    # ---- Feedback lifecycle ----

    def test_interaction_feedback_positive(self):
        interaction = self._make_interaction()
        interaction.feedback = "positive"
        self.assertEqual(interaction.feedback, "positive")

    def test_interaction_feedback_negative(self):
        interaction = self._make_interaction()
        interaction.feedback = "negative"
        self.assertEqual(interaction.feedback, "negative")

    def test_interaction_feedback_reset_to_none(self):
        interaction = self._make_interaction()
        interaction.feedback = "positive"
        interaction.feedback = "none"
        self.assertEqual(interaction.feedback, "none")

    # ---- Agent routing ----

    def test_interaction_routed_to_agent(self):
        interaction = self._make_interaction(agent_id=self.expense_agent.id)
        self.assertEqual(interaction.agent_id, self.expense_agent)

    def test_interaction_no_agent(self):
        """Interactions without an agent (e.g. informational direct query) are valid."""
        interaction = self._make_interaction()
        self.assertFalse(interaction.agent_id)

    # ---- Action log linkage ----

    def test_interaction_action_log_linkage(self):
        interaction = self._make_interaction(
            intent_type="transactional",
            query="Submit expense report EXP-001",
        )
        log = self.ActionLog.create({
            "user_id": self.env.user.id,
            "interaction_id": interaction.id,
            "intent_type": "transactional",
            "action_class": "approval_gated",
            "action_description": "Submitted expense report EXP-001",
            "outcome": "pending_approval",
        })
        self.assertIn(log, interaction.action_log_ids)

    def test_interaction_multiple_action_logs(self):
        interaction = self._make_interaction()
        for i in range(3):
            self.ActionLog.create({
                "user_id": self.env.user.id,
                "interaction_id": interaction.id,
                "intent_type": "informational",
                "action_class": "advisory",
                "action_description": f"Step {i}",
                "outcome": "success",
            })
        self.assertEqual(len(interaction.action_log_ids), 3)

    # ---- Tools invoked ----

    def test_interaction_tools_invoked_stored(self):
        interaction = self._make_interaction(
            tools_invoked="get_expense_status,get_project_budget",
        )
        self.assertIn("get_expense_status", interaction.tools_invoked)

    # ---- Duration ----

    def test_interaction_duration_stored(self):
        interaction = self._make_interaction(duration_ms=1250)
        self.assertEqual(interaction.duration_ms, 1250)

    # ---- Intent types ----

    def test_interaction_all_intent_types(self):
        for intent in ["informational", "navigational", "transactional"]:
            i = self._make_interaction(
                session_id=f"intent-test-{intent}",
                intent_type=intent,
            )
            self.assertEqual(i.intent_type, intent)
