"""Tests for ppm.scoring — investment scoring and project prioritization."""

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("ppm", "post_install", "-at_install")
class TestScoring(TransactionCase):
    """Test PPM scoring model: total score computation, weights, recommendation."""

    def setUp(self):
        super().setUp()
        self.project = self.env["project.project"].create({
            "name": "Test PPM Scoring Project",
        })
        self.Scoring = self.env["ppm.scoring"]

    def _make_scoring(self, **kwargs):
        defaults = {
            "project_id": self.project.id,
            "strategic_alignment": 3,
            "financial_benefit": 3,
            "risk_level": 3,
            "resource_availability": 3,
            "urgency": 3,
        }
        defaults.update(kwargs)
        return self.Scoring.create(defaults)

    def test_scoring_creation(self):
        """Scoring record can be created."""
        rec = self._make_scoring()
        self.assertTrue(rec.id)
        self.assertEqual(rec.project_id, self.project)

    def test_total_score_computation_all_medium(self):
        """Total score = sum of 5 dimensions (3+3+3+3+3 = 15)."""
        rec = self._make_scoring()
        self.assertAlmostEqual(rec.total_score, 15.0, places=1)

    def test_total_score_computation_max(self):
        """Maximum total score is 25 (5 per dimension × 5 dimensions)."""
        rec = self._make_scoring(
            strategic_alignment=5,
            financial_benefit=5,
            risk_level=5,
            resource_availability=5,
            urgency=5,
        )
        self.assertAlmostEqual(rec.total_score, 25.0, places=1)

    def test_total_score_computation_min(self):
        """Minimum total score is 5 (1 per dimension × 5 dimensions)."""
        rec = self._make_scoring(
            strategic_alignment=1,
            financial_benefit=1,
            risk_level=1,
            resource_availability=1,
            urgency=1,
        )
        self.assertAlmostEqual(rec.total_score, 5.0, places=1)

    def test_total_score_asymmetric(self):
        """Total score handles mixed dimension values correctly."""
        rec = self._make_scoring(
            strategic_alignment=5,
            financial_benefit=4,
            risk_level=2,
            resource_availability=3,
            urgency=1,
        )
        self.assertAlmostEqual(rec.total_score, 15.0, places=1)

    def test_total_score_recomputes_on_change(self):
        """Total score is recomputed when a dimension value changes."""
        rec = self._make_scoring()
        self.assertAlmostEqual(rec.total_score, 15.0, places=1)
        rec.write({"strategic_alignment": 5})
        self.assertAlmostEqual(rec.total_score, 17.0, places=1)

    def test_default_dimensions_are_3(self):
        """All scoring dimensions default to 3."""
        rec = self._make_scoring()
        self.assertEqual(rec.strategic_alignment, 3)
        self.assertEqual(rec.financial_benefit, 3)
        self.assertEqual(rec.risk_level, 3)
        self.assertEqual(rec.resource_availability, 3)
        self.assertEqual(rec.urgency, 3)

    def test_investment_type_options(self):
        """All investment types (run/change/grow) are accepted."""
        for itype in ("run", "change", "grow"):
            rec = self._make_scoring(investment_type=itype)
            self.assertEqual(rec.investment_type, itype)

    def test_recommendation_options(self):
        """All recommendation values are accepted."""
        for recom in ("proceed", "defer", "cancel", "review"):
            rec = self._make_scoring(recommendation=recom)
            self.assertEqual(rec.recommendation, recom)

    def test_scored_by_defaults_to_current_user(self):
        """scored_by_id defaults to the current user."""
        rec = self._make_scoring()
        self.assertEqual(rec.scored_by_id, self.env.user)

    def test_scored_date_defaults_to_today(self):
        """scored_date defaults to today."""
        from odoo import fields as odoo_fields
        rec = self._make_scoring()
        today = odoo_fields.Date.today()
        self.assertEqual(rec.scored_date, today)

    def test_company_inherited_from_project(self):
        """company_id is relayed from the linked project."""
        rec = self._make_scoring()
        self.assertEqual(rec.company_id, self.project.company_id)

    def test_notes_field(self):
        """Notes text can be stored on the scoring record."""
        rec = self._make_scoring(notes="Board approved prioritization.")
        self.assertEqual(rec.notes, "Board approved prioritization.")

    def test_ordering_by_total_score_descending(self):
        """Scoring records are ordered by total_score descending."""
        project2 = self.env["project.project"].create({"name": "Project B"})
        self._make_scoring(
            strategic_alignment=5, financial_benefit=5,
            risk_level=5, resource_availability=5, urgency=5,
        )
        self.Scoring.create({
            "project_id": project2.id,
            "strategic_alignment": 1,
            "financial_benefit": 1,
            "risk_level": 1,
            "resource_availability": 1,
            "urgency": 1,
        })
        recs = self.Scoring.search([])
        scores = [r.total_score for r in recs]
        self.assertEqual(scores, sorted(scores, reverse=True))
