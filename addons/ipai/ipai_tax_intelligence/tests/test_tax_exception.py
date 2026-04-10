"""Tests for tax.exception model and review state machine.

Covers full lifecycle transitions: detected → under_review → resolved,
waived, escalated, and reopen paths. Also verifies audit log is written
on every state transition.

Tagged with @tagged('tax', 'avatax', 'post_install', '-at_install')
"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("tax", "avatax", "post_install", "-at_install")
class TestTaxException(TransactionCase):
    """TransactionCase tests for tax.exception."""

    def setUp(self):
        super().setUp()
        self.Exception = self.env["tax.exception"]
        self.AuditLog = self.env["tax.audit.log"]
        self.ph_country = self.env.ref("base.ph")

        # Create a reusable blocking rule
        self.blocking_rule = self.env["tax.validation.rule"].create({
            "name": "Test Blocking Rule for Exceptions",
            "rule_type": "rate_check",
            "applies_to": "all",
            "severity": "blocking",
        })
        self.warning_rule = self.env["tax.validation.rule"].create({
            "name": "Test Warning Rule for Exceptions",
            "rule_type": "withholding_check",
            "applies_to": "bill",
            "severity": "warning",
        })

    def _make_exception(self, rule=None, **kwargs):
        """Helper to create a tax exception."""
        defaults = {
            "source_model": "account.move",
            "source_id": 999,
            "rule_id": (rule or self.blocking_rule).id,
            "exception_type": "rate_mismatch",
            "state": "detected",
        }
        defaults.update(kwargs)
        return self.Exception.create(defaults)

    def test_exception_created_with_correct_defaults(self):
        """Exception is created in detected state with a generated sequence name."""
        exc = self._make_exception()
        self.assertEqual(exc.state, "detected")
        self.assertTrue(exc.name)
        self.assertNotEqual(exc.name, "/")
        self.assertTrue(exc.name.startswith("TEXC/"))

    def test_exception_lifecycle_detected_to_under_review(self):
        """Exception moves from detected to under_review on action_start_review."""
        exc = self._make_exception()
        self.assertEqual(exc.state, "detected")
        exc.action_start_review()
        self.assertEqual(exc.state, "under_review")
        self.assertTrue(exc.reviewer_id)

    def test_exception_lifecycle_under_review_to_resolved(self):
        """Exception moves from under_review to resolved on action_resolve."""
        exc = self._make_exception()
        exc.action_start_review()
        exc.write({"resolution": "Tax rate corrected on invoice lines."})
        exc.action_resolve()
        self.assertEqual(exc.state, "resolved")
        self.assertTrue(exc.reviewer_id)
        self.assertTrue(exc.review_date)

    def test_exception_lifecycle_waived(self):
        """Exception can be waived from detected state."""
        exc = self._make_exception()
        exc.write({"resolution": "Management approved waiver — zero-rated supply."})
        exc.action_waive()
        self.assertEqual(exc.state, "waived")
        self.assertTrue(exc.review_date)

    def test_exception_lifecycle_escalated(self):
        """Exception can be escalated from under_review."""
        exc = self._make_exception()
        exc.action_start_review()
        exc.action_escalate()
        self.assertEqual(exc.state, "escalated")

    def test_exception_lifecycle_reopened_from_resolved(self):
        """Resolved exception can be reopened."""
        exc = self._make_exception()
        exc.action_start_review()
        exc.action_resolve()
        self.assertEqual(exc.state, "resolved")
        exc.action_reopen()
        self.assertEqual(exc.state, "detected")
        self.assertFalse(exc.reviewer_id)
        self.assertFalse(exc.review_date)

    def test_exception_lifecycle_reopened_from_waived(self):
        """Waived exception can be reopened."""
        exc = self._make_exception()
        exc.action_waive()
        exc.action_reopen()
        self.assertEqual(exc.state, "detected")

    def test_exception_audit_trail_on_state_change(self):
        """Each state transition creates an audit log entry."""
        exc = self._make_exception()
        initial_log_count = len(exc.audit_log_ids)  # created entry from creation
        self.assertGreaterEqual(initial_log_count, 1)

        exc.action_start_review()
        exc.action_resolve()

        # Should have at least 3 log entries: created, review_started, resolved
        self.assertGreaterEqual(len(exc.audit_log_ids), 3)

        actions = exc.audit_log_ids.mapped("action")
        self.assertIn("created", actions)
        self.assertIn("review_started", actions)
        self.assertIn("resolved", actions)

    def test_exception_severity_inherited_from_rule(self):
        """Exception severity is inherited from the linked rule."""
        exc = self._make_exception(rule=self.blocking_rule)
        self.assertEqual(exc.severity, "blocking")

        warning_exc = self._make_exception(rule=self.warning_rule)
        self.assertEqual(warning_exc.severity, "warning")

    def test_exception_explainability_fields(self):
        """Explainability fields are stored correctly."""
        exc = self._make_exception(
            rationale="No VAT applied to taxable line.",
            inputs_summary="Lines: 3. Without tax: 2.",
            confidence=0.95,
        )
        self.assertEqual(exc.rationale, "No VAT applied to taxable line.")
        self.assertEqual(exc.inputs_summary, "Lines: 3. Without tax: 2.")
        self.assertAlmostEqual(exc.confidence, 0.95, places=2)

    def test_exception_policy_reference_from_rule(self):
        """Policy reference is propagated from the linked rule."""
        rule_with_ref = self.env["tax.validation.rule"].create({
            "name": "Rule With Policy Ref For Test",
            "rule_type": "withholding_check",
            "applies_to": "bill",
            "severity": "blocking",
            "policy_reference": "NIRC Sec 57(B)",
        })
        exc = self._make_exception(rule=rule_with_ref)
        self.assertEqual(exc.policy_reference, "NIRC Sec 57(B)")
