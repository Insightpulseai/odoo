"""Tests for ppm.portfolio.health — RAG status and health scoring per project."""

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("ppm", "post_install", "-at_install")
class TestPortfolioHealth(TransactionCase):
    """Test PPM portfolio health model: RAG rollup, health score, lifecycle."""

    def setUp(self):
        super().setUp()
        self.project = self.env["project.project"].create({
            "name": "Test PPM Health Project",
        })
        self.Health = self.env["ppm.portfolio.health"]

    def _make_assessment(self, **kwargs):
        defaults = {
            "project_id": self.project.id,
            "assessment_date": "2026-01-15",
            "schedule_rag": "green",
            "budget_rag": "green",
            "scope_rag": "green",
            "resource_rag": "green",
        }
        defaults.update(kwargs)
        return self.Health.create(defaults)

    def test_assessment_creation(self):
        """Portfolio health assessment can be created."""
        rec = self._make_assessment()
        self.assertTrue(rec.id)
        self.assertEqual(rec.project_id, self.project)

    def test_overall_rag_all_green(self):
        """Overall RAG is green when all dimensions are green."""
        rec = self._make_assessment(
            schedule_rag="green", budget_rag="green",
            scope_rag="green", resource_rag="green",
        )
        self.assertEqual(rec.overall_rag, "green")

    def test_overall_rag_amber_when_any_amber(self):
        """Overall RAG is amber when at least one dimension is amber, none red."""
        rec = self._make_assessment(
            schedule_rag="green", budget_rag="amber",
            scope_rag="green", resource_rag="green",
        )
        self.assertEqual(rec.overall_rag, "amber")

    def test_overall_rag_red_when_any_red(self):
        """Overall RAG is red when at least one dimension is red."""
        rec = self._make_assessment(
            schedule_rag="red", budget_rag="green",
            scope_rag="green", resource_rag="green",
        )
        self.assertEqual(rec.overall_rag, "red")

    def test_overall_rag_red_takes_priority_over_amber(self):
        """Red takes priority over amber in overall RAG computation."""
        rec = self._make_assessment(
            schedule_rag="amber", budget_rag="red",
            scope_rag="amber", resource_rag="green",
        )
        self.assertEqual(rec.overall_rag, "red")

    def test_health_score_all_green_is_100(self):
        """Health score is 100 when all dimensions are green."""
        rec = self._make_assessment(
            schedule_rag="green", budget_rag="green",
            scope_rag="green", resource_rag="green",
        )
        self.assertAlmostEqual(rec.health_score, 100.0, places=1)

    def test_health_score_all_red_is_0(self):
        """Health score is 0 when all dimensions are red."""
        rec = self._make_assessment(
            schedule_rag="red", budget_rag="red",
            scope_rag="red", resource_rag="red",
        )
        self.assertAlmostEqual(rec.health_score, 0.0, places=1)

    def test_health_score_mixed(self):
        """Health score is average of dimension scores (green=100, amber=50, red=0)."""
        rec = self._make_assessment(
            schedule_rag="green", budget_rag="amber",
            scope_rag="red", resource_rag="green",
        )
        # (100 + 50 + 0 + 100) / 4 = 62.5
        self.assertAlmostEqual(rec.health_score, 62.5, places=1)

    def test_health_score_boundaries(self):
        """Health score stays within 0-100 range for all combinations."""
        for combo in [
            ("green", "green", "green", "amber"),
            ("amber", "amber", "amber", "amber"),
            ("red", "amber", "green", "green"),
        ]:
            rec = self._make_assessment(
                schedule_rag=combo[0], budget_rag=combo[1],
                scope_rag=combo[2], resource_rag=combo[3],
            )
            self.assertGreaterEqual(rec.health_score, 0.0)
            self.assertLessEqual(rec.health_score, 100.0)

    def test_default_assessor_is_current_user(self):
        """Assessor defaults to the current user."""
        rec = self._make_assessment()
        self.assertEqual(rec.assessor_id, self.env.user)

    def test_commentary_field(self):
        """Commentary text can be stored on the assessment."""
        rec = self._make_assessment(commentary="Budget overspend due to scope creep.")
        self.assertEqual(rec.commentary, "Budget overspend due to scope creep.")

    def test_company_id_inherited_from_project(self):
        """company_id is relayed from the linked project."""
        rec = self._make_assessment()
        self.assertEqual(rec.company_id, self.project.company_id)

    def test_rag_selection_options(self):
        """All valid RAG values (green, amber, red) are accepted."""
        for rag in ("green", "amber", "red"):
            rec = self._make_assessment(schedule_rag=rag)
            self.assertEqual(rec.schedule_rag, rag)
