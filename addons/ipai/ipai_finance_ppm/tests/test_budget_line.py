"""Tests for ppm.budget.line — budget/forecast/actual per project per period."""

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("ppm", "post_install", "-at_install")
class TestBudgetLine(TransactionCase):
    """Test PPM budget line model: computed fields, constraints, lifecycle."""

    def setUp(self):
        super().setUp()
        self.project = self.env["project.project"].create({
            "name": "Test PPM Budget Project",
        })
        self.BudgetLine = self.env["ppm.budget.line"]

    def _make_line(self, **kwargs):
        defaults = {
            "project_id": self.project.id,
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
            "budget_amount": 10000.0,
            "forecast_amount": 9500.0,
            "actual_amount": 8000.0,
        }
        defaults.update(kwargs)
        return self.BudgetLine.create(defaults)

    def test_budget_line_creation(self):
        """Budget line can be created with required fields."""
        line = self._make_line()
        self.assertTrue(line.id)
        self.assertEqual(line.project_id, self.project)
        self.assertEqual(line.budget_amount, 10000.0)

    def test_variance_computation(self):
        """Variance = budget - actual; variance_pct is correctly computed."""
        line = self._make_line(budget_amount=10000.0, actual_amount=8000.0)
        self.assertAlmostEqual(line.variance, 2000.0, places=2)
        self.assertAlmostEqual(line.variance_pct, 20.0, places=2)

    def test_variance_negative_when_over_budget(self):
        """Negative variance when actual exceeds budget."""
        line = self._make_line(budget_amount=10000.0, actual_amount=12000.0)
        self.assertAlmostEqual(line.variance, -2000.0, places=2)
        self.assertAlmostEqual(line.variance_pct, -20.0, places=2)

    def test_variance_zero_budget(self):
        """Variance pct is 0.0 when budget is 0 (no division by zero)."""
        line = self._make_line(budget_amount=0.0, actual_amount=0.0)
        self.assertAlmostEqual(line.variance_pct, 0.0, places=2)

    def test_period_label_computed(self):
        """Period label is computed as YYYY-MM from period_start."""
        line = self._make_line(period_start="2026-03-01")
        self.assertEqual(line.period_label, "2026-03")

    def test_period_label_empty_without_start(self):
        """Period label is empty string when period_start is not set."""
        line = self._make_line()
        # Force period_start to False to test the else branch
        line.write({"period_start": False})
        line._compute_period_label()
        self.assertEqual(line.period_label, "")

    def test_cost_type_default(self):
        """Default cost type is opex."""
        line = self._make_line()
        self.assertEqual(line.cost_type, "opex")

    def test_cost_type_capex(self):
        """CAPEX cost type can be set."""
        line = self._make_line(cost_type="capex")
        self.assertEqual(line.cost_type, "capex")

    def test_company_id_inherited_from_project(self):
        """company_id is relayed from the project."""
        line = self._make_line()
        self.assertEqual(line.company_id, self.project.company_id)

    def test_unique_constraint_different_cost_types(self):
        """Two lines for the same project/period but different cost type is allowed."""
        self._make_line(cost_type="capex")
        # Should not raise
        self._make_line(cost_type="opex")

    def test_notes_field(self):
        """Notes can be stored on a budget line."""
        line = self._make_line(notes="Approved by board 2026-01-10")
        self.assertEqual(line.notes, "Approved by board 2026-01-10")

    def test_ordering_by_project_then_period(self):
        """Lines are ordered by project then period_start."""
        self._make_line(period_start="2026-03-01", period_end="2026-03-31")
        self._make_line(period_start="2026-01-01", period_end="2026-01-31")
        lines = self.BudgetLine.search([("project_id", "=", self.project.id)])
        starts = [str(l.period_start) for l in lines]
        self.assertEqual(starts, sorted(starts))
