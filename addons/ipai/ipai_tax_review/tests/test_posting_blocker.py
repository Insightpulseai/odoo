"""Tests for posting blocker — Constitution C2.5.

Verify that account.move.action_post() is blocked when there are
unresolved tax review findings (needs_review or rejected).
"""

from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged("-at_install", "post_install")
class TestPostingBlocker(TransactionCase):
    """Test that posting is blocked by unresolved tax reviews."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Blocker Test Vendor"})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )

    def _create_bill(self):
        return self.env["account.move"].create({
            "move_type": "in_invoice",
            "partner_id": self.partner.id,
            "journal_id": self.journal.id,
            "invoice_line_ids": [(0, 0, {
                "name": "Service line",
                "quantity": 1,
                "price_unit": 50000.0,
            })],
        })

    def _create_review(self, move, state="needs_review"):
        return self.env["ipai.tax.review"].create({
            "move_id": move.id,
            "state": state,
            "expected_payable": 50000.0,
            "printed_total_due": 50000.0,
            "delta": 0.0,
        })

    def test_post_blocked_needs_review(self):
        """Posting blocked when review is needs_review."""
        move = self._create_bill()
        self._create_review(move, state="needs_review")
        with self.assertRaises(UserError):
            move.action_post()

    def test_post_blocked_rejected(self):
        """Posting blocked when review is rejected."""
        move = self._create_bill()
        self._create_review(move, state="rejected")
        with self.assertRaises(UserError):
            move.action_post()

    def test_post_allowed_validated(self):
        """Posting allowed when review is validated."""
        move = self._create_bill()
        self._create_review(move, state="validated")
        # Should not raise — posting proceeds
        move.action_post()
        self.assertEqual(move.state, "posted")

    def test_post_allowed_overridden(self):
        """Posting allowed when review is overridden."""
        move = self._create_bill()
        self._create_review(move, state="overridden")
        move.action_post()
        self.assertEqual(move.state, "posted")

    def test_post_allowed_no_reviews(self):
        """Posting allowed when there are no reviews at all."""
        move = self._create_bill()
        move.action_post()
        self.assertEqual(move.state, "posted")

    def test_post_blocked_mixed_reviews(self):
        """Posting blocked if any review is blocking, even with validated ones."""
        move = self._create_bill()
        self._create_review(move, state="validated")
        self._create_review(move, state="needs_review")
        with self.assertRaises(UserError):
            move.action_post()
