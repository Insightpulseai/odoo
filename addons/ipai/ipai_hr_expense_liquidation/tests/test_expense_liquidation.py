# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged("post_install", "-at_install")
class TestExpenseLiquidation(TransactionCase):
    """Test hr.expense.liquidation model and state machine."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({
            "name": "Test Employee",
        })

    def _create_liquidation(self, **kwargs):
        """Helper: create a liquidation with defaults."""
        vals = {
            "employee_id": self.employee.id,
            "liquidation_type": "reimbursement",
            "advance_amount": 5000.0,
        }
        vals.update(kwargs)
        return self.env["hr.expense.liquidation"].create(vals)

    # --- Creation ---

    def test_create_generates_sequence(self):
        """Liquidation must auto-generate a LIQ/YYYY/XXXXX reference."""
        liq = self._create_liquidation()
        self.assertTrue(liq.name, "Name should be auto-generated")
        self.assertTrue(
            liq.name.startswith("LIQ/"),
            "Name should start with LIQ/ prefix, got: %s" % liq.name,
        )

    def test_create_default_state_is_draft(self):
        """New liquidation must start in draft state."""
        liq = self._create_liquidation()
        self.assertEqual(liq.state, "draft")

    def test_create_default_type_is_reimbursement(self):
        """Default liquidation type should be reimbursement."""
        liq = self.env["hr.expense.liquidation"].create({
            "employee_id": self.employee.id,
        })
        self.assertEqual(liq.liquidation_type, "reimbursement")

    # --- State transitions ---

    def test_submit_sets_state_and_date(self):
        """action_submit must transition to submitted and set date."""
        liq = self._create_liquidation()
        liq.action_submit()
        self.assertEqual(liq.state, "submitted")
        self.assertTrue(liq.date_submit, "date_submit should be set")

    def test_approve_from_submitted(self):
        """action_approve must transition from submitted to approved."""
        liq = self._create_liquidation()
        liq.action_submit()
        liq.action_approve()
        self.assertEqual(liq.state, "approved")
        self.assertTrue(liq.date_approve, "date_approve should be set")

    def test_done_from_approved(self):
        """action_done must transition from approved to done."""
        liq = self._create_liquidation()
        liq.action_submit()
        liq.action_approve()
        liq.action_done()
        self.assertEqual(liq.state, "done")

    def test_reject_from_submitted(self):
        """action_reject must transition to rejected."""
        liq = self._create_liquidation()
        liq.action_submit()
        liq.action_reject()
        self.assertEqual(liq.state, "rejected")

    def test_cancel(self):
        """action_cancel must transition to cancelled."""
        liq = self._create_liquidation()
        liq.action_cancel()
        self.assertEqual(liq.state, "cancelled")

    def test_reset_to_draft_from_rejected(self):
        """action_draft must reset rejected liquidation to draft."""
        liq = self._create_liquidation()
        liq.action_submit()
        liq.action_reject()
        liq.action_draft()
        self.assertEqual(liq.state, "draft")

    def test_reset_to_draft_from_cancelled(self):
        """action_draft must reset cancelled liquidation to draft."""
        liq = self._create_liquidation()
        liq.action_cancel()
        liq.action_draft()
        self.assertEqual(liq.state, "draft")

    # --- Computed fields ---

    def test_total_expenses_computed(self):
        """total_expenses must sum line item amounts."""
        liq = self._create_liquidation(advance_amount=10000.0)
        self.env["hr.expense.liquidation.line"].create([
            {
                "liquidation_id": liq.id,
                "name": "Taxi",
                "amount": 500.0,
                "category": "transport",
            },
            {
                "liquidation_id": liq.id,
                "name": "Lunch",
                "amount": 300.0,
                "category": "meals",
            },
        ])
        liq.invalidate_recordset()
        self.assertAlmostEqual(liq.total_expenses, 800.0)

    def test_balance_computed(self):
        """balance must equal advance_amount minus total_expenses."""
        liq = self._create_liquidation(advance_amount=5000.0)
        self.env["hr.expense.liquidation.line"].create({
            "liquidation_id": liq.id,
            "name": "Hotel",
            "amount": 3000.0,
            "category": "accommodation",
        })
        liq.invalidate_recordset()
        self.assertAlmostEqual(liq.balance, 2000.0)

    def test_zero_lines_zero_total(self):
        """Liquidation with no lines must have zero total_expenses."""
        liq = self._create_liquidation()
        self.assertAlmostEqual(liq.total_expenses, 0.0)
        self.assertAlmostEqual(liq.balance, liq.advance_amount)

    # --- Line items ---

    def test_line_item_creation(self):
        """Expense line items must be creatable with all categories."""
        liq = self._create_liquidation()
        for cat in ("meals", "transport", "accommodation", "supplies", "misc"):
            line = self.env["hr.expense.liquidation.line"].create({
                "liquidation_id": liq.id,
                "name": "Test %s" % cat,
                "amount": 100.0,
                "category": cat,
            })
            self.assertEqual(line.category, cat)

    def test_line_cascade_delete(self):
        """Deleting liquidation must cascade-delete line items."""
        liq = self._create_liquidation()
        line = self.env["hr.expense.liquidation.line"].create({
            "liquidation_id": liq.id,
            "name": "Test line",
            "amount": 100.0,
        })
        line_id = line.id
        liq.unlink()
        remaining = self.env["hr.expense.liquidation.line"].search([
            ("id", "=", line_id),
        ])
        self.assertFalse(remaining, "Line items should cascade-delete")


@tagged("post_install", "-at_install")
class TestExpensePolicyRule(TransactionCase):
    """Test hr.expense.policy.rule model."""

    def test_create_amount_limit_rule(self):
        """Amount limit policy rule must be creatable."""
        rule = self.env["hr.expense.policy.rule"].create({
            "name": "Max single expense 10K",
            "rule_type": "amount_limit",
            "amount_limit": 10000.0,
            "severity": "blocking",
        })
        self.assertEqual(rule.rule_type, "amount_limit")
        self.assertAlmostEqual(rule.amount_limit, 10000.0)

    def test_create_receipt_required_rule(self):
        """Receipt required policy rule must be creatable."""
        rule = self.env["hr.expense.policy.rule"].create({
            "name": "Receipt required over 500",
            "rule_type": "receipt_required",
            "amount_limit": 500.0,
            "severity": "warning",
        })
        self.assertEqual(rule.rule_type, "receipt_required")

    def test_create_category_limit_rule(self):
        """Category limit policy rule must be creatable."""
        rule = self.env["hr.expense.policy.rule"].create({
            "name": "Meals max 2000",
            "rule_type": "category_limit",
            "category": "meals",
            "amount_limit": 2000.0,
        })
        self.assertEqual(rule.category, "meals")

    def test_rule_default_severity_is_warning(self):
        """Default severity must be warning."""
        rule = self.env["hr.expense.policy.rule"].create({
            "name": "Test rule",
            "rule_type": "amount_limit",
        })
        self.assertEqual(rule.severity, "warning")

    def test_rule_ordering_by_sequence(self):
        """Rules must be ordered by sequence field."""
        rule_a = self.env["hr.expense.policy.rule"].create({
            "name": "Rule A",
            "rule_type": "amount_limit",
            "sequence": 20,
        })
        rule_b = self.env["hr.expense.policy.rule"].create({
            "name": "Rule B",
            "rule_type": "amount_limit",
            "sequence": 10,
        })
        rules = self.env["hr.expense.policy.rule"].search([
            ("id", "in", [rule_a.id, rule_b.id]),
        ])
        self.assertEqual(
            rules[0].id,
            rule_b.id,
            "Rule B (seq=10) should come before Rule A (seq=20)",
        )
