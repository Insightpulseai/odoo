"""Tests for ppm.risk — project risk register."""

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("ppm", "post_install", "-at_install")
class TestRisk(TransactionCase):
    """Test PPM risk model: score computation, lifecycle, project linkage."""

    def setUp(self):
        super().setUp()
        self.project = self.env["project.project"].create({
            "name": "Test PPM Risk Project",
        })
        self.Risk = self.env["ppm.risk"]

    def _make_risk(self, **kwargs):
        defaults = {
            "name": "Test Risk",
            "project_id": self.project.id,
            "probability": "3",
            "impact": "3",
        }
        defaults.update(kwargs)
        return self.Risk.create(defaults)

    def test_risk_creation(self):
        """Risk record can be created with required fields."""
        risk = self._make_risk()
        self.assertTrue(risk.id)
        self.assertEqual(risk.name, "Test Risk")
        self.assertEqual(risk.project_id, self.project)

    def test_risk_project_link(self):
        """Risk is linked to its project."""
        risk = self._make_risk()
        self.assertEqual(risk.project_id.id, self.project.id)

    def test_risk_score_computation_medium(self):
        """Risk score = probability * impact (3 * 3 = 9)."""
        risk = self._make_risk(probability="3", impact="3")
        self.assertEqual(risk.risk_score, 9)

    def test_risk_score_computation_max(self):
        """Maximum risk score is 25 (5 * 5)."""
        risk = self._make_risk(probability="5", impact="5")
        self.assertEqual(risk.risk_score, 25)

    def test_risk_score_computation_min(self):
        """Minimum risk score is 1 (1 * 1)."""
        risk = self._make_risk(probability="1", impact="1")
        self.assertEqual(risk.risk_score, 1)

    def test_risk_score_asymmetric(self):
        """Risk score handles asymmetric probability/impact correctly."""
        risk = self._make_risk(probability="4", impact="2")
        self.assertEqual(risk.risk_score, 8)

    def test_risk_lifecycle_identified_to_mitigating(self):
        """Risk can move from identified to mitigating state."""
        risk = self._make_risk()
        self.assertEqual(risk.state, "identified")
        risk.write({"state": "mitigating"})
        self.assertEqual(risk.state, "mitigating")

    def test_risk_lifecycle_mitigating_to_closed(self):
        """Risk can move from mitigating to closed state."""
        risk = self._make_risk(state="mitigating")
        risk.write({"state": "closed"})
        self.assertEqual(risk.state, "closed")

    def test_risk_lifecycle_assessed_state(self):
        """Risk can be set to assessed state."""
        risk = self._make_risk()
        risk.write({"state": "assessed"})
        self.assertEqual(risk.state, "assessed")

    def test_risk_lifecycle_accepted_state(self):
        """Risk can be accepted without mitigation."""
        risk = self._make_risk()
        risk.write({"state": "accepted"})
        self.assertEqual(risk.state, "accepted")

    def test_risk_default_state_is_identified(self):
        """Default state is identified."""
        risk = self._make_risk()
        self.assertEqual(risk.state, "identified")

    def test_risk_default_probability_and_impact(self):
        """Default probability and impact are both medium (3)."""
        risk = self._make_risk()
        self.assertEqual(risk.probability, "3")
        self.assertEqual(risk.impact, "3")

    def test_risk_owner_assignment(self):
        """Risk owner can be assigned."""
        user = self.env.user
        risk = self._make_risk(owner_id=user.id)
        self.assertEqual(risk.owner_id, user)

    def test_risk_mitigation_plan(self):
        """Mitigation plan text can be stored."""
        risk = self._make_risk(mitigation_plan="Implement redundant systems.")
        self.assertEqual(risk.mitigation_plan, "Implement redundant systems.")

    def test_risk_category_options(self):
        """All risk categories are accepted."""
        for cat in ("financial", "schedule", "resource", "technical", "compliance", "external"):
            risk = self._make_risk(category=cat)
            self.assertEqual(risk.category, cat)

    def test_risk_ordering_by_score_descending(self):
        """Risks are ordered by risk_score descending."""
        low = self._make_risk(name="Low Risk", probability="1", impact="1")
        high = self._make_risk(name="High Risk", probability="5", impact="5")
        risks = self.Risk.search([("project_id", "=", self.project.id)])
        scores = [r.risk_score for r in risks]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_risk_company_inherited_from_project(self):
        """company_id is relayed from the linked project."""
        risk = self._make_risk()
        self.assertEqual(risk.company_id, self.project.company_id)
