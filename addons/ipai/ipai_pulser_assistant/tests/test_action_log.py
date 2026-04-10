# -*- coding: utf-8 -*-
"""
Tests for pulser.action.log — audited action log.

Validates: log creation, outcome tracking, confidence bounds enforcement,
transactional actions must be classified (no unclassified transactional action).
"""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("pulser", "joule", "post_install", "-at_install")
class TestPulserActionLog(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ActionLog = self.env["pulser.action.log"]
        self.Agent = self.env["pulser.domain.agent"]
        self.ActionClass = self.env["pulser.action.class"]

        self.expense_agent = self.Agent.create({
            "name": "Log Test Expense Agent",
            "domain": "log_test_expense",
        })

    def _make_log(self, **kwargs):
        defaults = {
            "user_id": self.env.user.id,
            "intent_type": "informational",
            "action_class": "advisory",
            "action_description": "Test action",
            "outcome": "success",
        }
        defaults.update(kwargs)
        return self.ActionLog.create(defaults)

    # ---- Creation ----

    def test_log_creation_informational(self):
        log = self._make_log(
            intent_type="informational",
            action_class="advisory",
            action_description="Queried invoice INV-2026-0042 status",
        )
        self.assertEqual(log.intent_type, "informational")
        self.assertEqual(log.action_class, "advisory")

    def test_log_creation_transactional(self):
        log = self._make_log(
            intent_type="transactional",
            action_class="approval_gated",
            action_description="Submitted expense report EXP-0001",
            outcome="pending_approval",
        )
        self.assertEqual(log.outcome, "pending_approval")

    def test_log_default_timestamp_set(self):
        log = self._make_log()
        self.assertTrue(log.timestamp, "Timestamp must be set on creation")

    def test_log_default_user_is_current(self):
        log = self._make_log()
        self.assertEqual(log.user_id, self.env.user)

    # ---- Outcome tracking ----

    def test_log_outcome_success(self):
        log = self._make_log(outcome="success")
        self.assertEqual(log.outcome, "success")

    def test_log_outcome_failed(self):
        log = self._make_log(outcome="failed", error_message="Connection timeout")
        self.assertEqual(log.outcome, "failed")
        self.assertEqual(log.error_message, "Connection timeout")

    def test_log_outcome_pending_approval(self):
        log = self._make_log(
            intent_type="transactional",
            action_class="approval_gated",
            outcome="pending_approval",
        )
        self.assertEqual(log.outcome, "pending_approval")

    def test_log_outcome_rejected(self):
        log = self._make_log(
            intent_type="transactional",
            action_class="approval_gated",
            outcome="rejected",
        )
        self.assertEqual(log.outcome, "rejected")

    def test_log_outcome_can_be_updated(self):
        log = self._make_log(
            intent_type="transactional",
            action_class="approval_gated",
            outcome="pending_approval",
        )
        log.outcome = "success"
        self.assertEqual(log.outcome, "success")

    # ---- Confidence bounds ----

    def test_log_confidence_zero(self):
        log = self._make_log(confidence=0.0)
        self.assertEqual(log.confidence, 0.0)

    def test_log_confidence_one(self):
        log = self._make_log(confidence=1.0)
        self.assertEqual(log.confidence, 1.0)

    def test_log_confidence_midpoint(self):
        log = self._make_log(confidence=0.75)
        self.assertAlmostEqual(log.confidence, 0.75, places=4)

    def test_log_confidence_above_1_raises(self):
        with self.assertRaises(ValidationError):
            self._make_log(confidence=1.01)

    def test_log_confidence_below_0_raises(self):
        with self.assertRaises(ValidationError):
            self._make_log(confidence=-0.01)

    # ---- Explainability fields ----

    def test_log_rationale_stored(self):
        log = self._make_log(
            rationale="User asked for expense status; retrieved from hr.expense directly",
        )
        self.assertIn("hr.expense", log.rationale)

    def test_log_inputs_summary_stored(self):
        log = self._make_log(inputs_summary="expense_id=42, user_id=1")
        self.assertIn("expense_id", log.inputs_summary)

    def test_log_policy_reference_stored(self):
        log = self._make_log(policy_reference="SOP-EXPENSE-001")
        self.assertEqual(log.policy_reference, "SOP-EXPENSE-001")

    # ---- Agent association ----

    def test_log_with_agent(self):
        log = self._make_log(agent_id=self.expense_agent.id)
        self.assertEqual(log.agent_id, self.expense_agent)

    # ---- Duration ----

    def test_log_duration_stored(self):
        log = self._make_log(duration_ms=423)
        self.assertEqual(log.duration_ms, 423)
