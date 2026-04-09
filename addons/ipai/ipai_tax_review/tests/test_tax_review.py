"""Tests for ipai.tax.review model — state transitions and review workflow."""

from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged("-at_install", "post_install")
class TestTaxReview(TransactionCase):
    """Test tax review creation, state transitions, and wizard override."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Vendor PH"})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )
        cls.move = cls.env["account.move"].create({
            "move_type": "in_invoice",
            "partner_id": cls.partner.id,
            "journal_id": cls.journal.id,
            "invoice_line_ids": [(0, 0, {
                "name": "Test service",
                "quantity": 1,
                "price_unit": 100000.0,
            })],
        })

    def _create_review(self, state="needs_review", **kwargs):
        vals = {
            "move_id": self.move.id,
            "state": state,
            "expected_subtotal": 100000.0,
            "expected_vat": 12000.0,
            "expected_gross": 112000.0,
            "expected_withholding": 2000.0,
            "expected_payable": 110000.0,
            "printed_total_due": 110000.0,
            "delta": 0.0,
            "extraction_confidence": 0.97,
            "explanation_summary": "All checks passed.",
        }
        vals.update(kwargs)
        return self.env["ipai.tax.review"].create(vals)

    def test_create_review_default_state(self):
        """New review defaults to needs_review."""
        review = self._create_review()
        self.assertEqual(review.state, "needs_review")
        self.assertTrue(review.name, "Review should have a sequence reference")

    def test_override_opens_wizard(self):
        """action_override returns wizard action, not direct write."""
        review = self._create_review()
        result = review.action_override()
        self.assertEqual(result["res_model"], "ipai.tax.review.override.wizard")
        self.assertEqual(result["target"], "new")

    def test_wizard_override_with_reason(self):
        """Override wizard writes state + reason + reviewer."""
        review = self._create_review()
        wizard = self.env["ipai.tax.review.override.wizard"].create({
            "review_id": review.id,
            "override_reason": "Verified manually with supplier.",
        })
        wizard.action_confirm_override()
        self.assertEqual(review.state, "overridden")
        self.assertEqual(review.override_reason, "Verified manually with supplier.")
        self.assertTrue(review.reviewer_id)
        self.assertTrue(review.reviewed_date)

    def test_wizard_override_empty_reason_raises(self):
        """Override wizard rejects empty reason."""
        review = self._create_review()
        wizard = self.env["ipai.tax.review.override.wizard"].create({
            "review_id": review.id,
            "override_reason": "   ",
        })
        with self.assertRaises(UserError):
            wizard.action_confirm_override()

    def test_reject_sets_state(self):
        """action_reject transitions to rejected."""
        review = self._create_review()
        review.action_reject()
        self.assertEqual(review.state, "rejected")
        self.assertTrue(review.reviewer_id)

    def test_reset_to_review(self):
        """action_reset_to_review clears reviewer and returns to needs_review."""
        review = self._create_review()
        review.action_reject()
        review.action_reset_to_review()
        self.assertEqual(review.state, "needs_review")
        self.assertFalse(review.reviewer_id)
        self.assertFalse(review.reviewed_date)

    def test_request_explanation_creates_record(self):
        """action_request_explanation creates an explanation record."""
        review = self._create_review()
        review.action_request_explanation()
        self.assertEqual(review.explanation_count, 1)
        explanation = review.explanation_ids[0]
        self.assertEqual(explanation.model_id, "pending")

    def test_smart_button_count(self):
        """tax_review_count on account.move reflects linked reviews."""
        self._create_review()
        self._create_review(state="validated")
        self.assertEqual(self.move.tax_review_count, 2)

    def test_view_tax_reviews_action(self):
        """action_view_tax_reviews returns correct domain."""
        self._create_review()
        action = self.move.action_view_tax_reviews()
        self.assertEqual(action["domain"], [("move_id", "=", self.move.id)])
