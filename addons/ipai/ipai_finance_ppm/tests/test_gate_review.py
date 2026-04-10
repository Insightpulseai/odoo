"""Tests for ppm.gate.review — phase-gate review governance for projects."""

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("ppm", "post_install", "-at_install")
class TestGateReview(TransactionCase):
    """Test PPM gate review model: outcomes, sequencing, reviewer assignment."""

    def setUp(self):
        super().setUp()
        self.project = self.env["project.project"].create({
            "name": "Test PPM Gate Project",
        })
        self.GateReview = self.env["ppm.gate.review"]

    def _make_gate(self, **kwargs):
        defaults = {
            "name": "Initiation Gate",
            "project_id": self.project.id,
            "gate_type": "initiation",
            "gate_date": "2026-02-01",
        }
        defaults.update(kwargs)
        return self.GateReview.create(defaults)

    def test_gate_review_creation(self):
        """Gate review record can be created."""
        gate = self._make_gate()
        self.assertTrue(gate.id)
        self.assertEqual(gate.project_id, self.project)

    def test_default_state_is_scheduled(self):
        """Default state is scheduled."""
        gate = self._make_gate()
        self.assertEqual(gate.state, "scheduled")

    def test_gate_review_outcomes_all_valid(self):
        """All gate outcome states are accepted."""
        for outcome in ("scheduled", "in_progress", "passed", "conditional", "failed", "deferred"):
            gate = self._make_gate(state=outcome)
            self.assertEqual(gate.state, outcome)

    def test_action_pass_sets_state_and_date(self):
        """action_pass() sets state to passed and records decision_date."""
        gate = self._make_gate()
        gate.action_pass()
        self.assertEqual(gate.state, "passed")
        self.assertTrue(gate.decision_date)
        self.assertTrue(gate.decided_by_id)

    def test_action_conditional_pass(self):
        """action_conditional_pass() sets state to conditional."""
        gate = self._make_gate(conditions="Must resolve all critical risks first.")
        gate.action_conditional_pass()
        self.assertEqual(gate.state, "conditional")
        self.assertTrue(gate.decision_date)

    def test_action_fail(self):
        """action_fail() sets state to failed."""
        gate = self._make_gate()
        gate.action_fail()
        self.assertEqual(gate.state, "failed")
        self.assertTrue(gate.decision_date)

    def test_decided_by_is_current_user_on_pass(self):
        """decided_by_id is set to current user when gate is passed."""
        gate = self._make_gate()
        gate.action_pass()
        self.assertEqual(gate.decided_by_id, self.env.user)

    def test_gate_type_options(self):
        """All gate types are accepted."""
        for gtype in ("initiation", "planning", "execution", "monitoring", "closure"):
            gate = self._make_gate(gate_type=gtype)
            self.assertEqual(gate.gate_type, gtype)

    def test_reviewer_assignment(self):
        """Multiple reviewers can be assigned to a gate."""
        user1 = self.env["res.users"].sudo().create({
            "name": "Gate Reviewer 1",
            "login": "gate_reviewer1@test.com",
        })
        user2 = self.env["res.users"].sudo().create({
            "name": "Gate Reviewer 2",
            "login": "gate_reviewer2@test.com",
        })
        gate = self._make_gate()
        gate.write({"reviewer_ids": [(4, user1.id), (4, user2.id)]})
        self.assertIn(user1, gate.reviewer_ids)
        self.assertIn(user2, gate.reviewer_ids)

    def test_reviewer_assignment_empty_by_default(self):
        """Reviewer list is empty by default."""
        gate = self._make_gate()
        self.assertEqual(len(gate.reviewer_ids), 0)

    def test_gate_sequence_ordering(self):
        """Gates are ordered by gate_date descending (most recent first)."""
        self._make_gate(name="First Gate", gate_date="2026-01-01")
        self._make_gate(name="Later Gate", gate_date="2026-06-01")
        gates = self.GateReview.search([("project_id", "=", self.project.id)])
        dates = [str(g.gate_date) for g in gates]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_gate_criteria_stored(self):
        """Gate criteria text is stored and retrievable."""
        gate = self._make_gate(criteria="Business case signed off. Budget approved.")
        self.assertEqual(gate.criteria, "Business case signed off. Budget approved.")

    def test_gate_findings_stored(self):
        """Gate findings text is stored and retrievable."""
        gate = self._make_gate()
        gate.write({"findings": "Three open risks require mitigation plans."})
        self.assertEqual(gate.findings, "Three open risks require mitigation plans.")

    def test_gate_conditions_for_conditional_pass(self):
        """Conditions text is stored for conditional pass records."""
        gate = self._make_gate(conditions="Close all P1 issues before next sprint.")
        self.assertEqual(gate.conditions, "Close all P1 issues before next sprint.")

    def test_company_inherited_from_project(self):
        """company_id is relayed from the linked project."""
        gate = self._make_gate()
        self.assertEqual(gate.company_id, self.project.company_id)

    def test_gate_project_link(self):
        """Gate review is correctly linked to its project."""
        gate = self._make_gate()
        self.assertEqual(gate.project_id.id, self.project.id)

    def test_multiple_gates_per_project(self):
        """Multiple gates can be created for a single project."""
        g1 = self._make_gate(name="Gate A", gate_type="initiation", gate_date="2026-01-01")
        g2 = self._make_gate(name="Gate B", gate_type="planning", gate_date="2026-03-01")
        gates = self.GateReview.search([("project_id", "=", self.project.id)])
        self.assertEqual(len(gates), 2)
