"""Tests for tax.audit.log model.

Verifies audit log creation on exception creation and state transitions.

Tagged with @tagged('tax', 'avatax', 'post_install', '-at_install')
"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("tax", "avatax", "post_install", "-at_install")
class TestTaxAuditLog(TransactionCase):
    """TransactionCase tests for tax.audit.log."""

    def setUp(self):
        super().setUp()
        self.AuditLog = self.env["tax.audit.log"]
        self.Exception = self.env["tax.exception"]

        self.rule = self.env["tax.validation.rule"].create({
            "name": "Audit Log Test Rule",
            "rule_type": "rate_check",
            "applies_to": "all",
            "severity": "blocking",
        })

    def _make_exception(self, **kwargs):
        defaults = {
            "source_model": "account.move",
            "source_id": 1,
            "rule_id": self.rule.id,
            "exception_type": "rate_mismatch",
        }
        defaults.update(kwargs)
        return self.Exception.create(defaults)

    def test_audit_log_created_on_exception_creation(self):
        """Creating a tax exception automatically creates a 'created' audit log entry."""
        exc = self._make_exception()
        logs = exc.audit_log_ids
        self.assertGreater(len(logs), 0, "Audit log must be created on exception creation.")

        created_log = logs.filtered(lambda l: l.action == "created")
        self.assertEqual(len(created_log), 1)
        self.assertEqual(created_log.exception_id, exc)
        self.assertEqual(created_log.new_state, "detected")
        self.assertFalse(created_log.old_state)

    def test_audit_log_on_start_review(self):
        """action_start_review writes a review_started audit log."""
        exc = self._make_exception()
        exc.action_start_review()

        review_log = exc.audit_log_ids.filtered(lambda l: l.action == "review_started")
        self.assertEqual(len(review_log), 1)
        self.assertEqual(review_log.old_state, "detected")
        self.assertEqual(review_log.new_state, "under_review")

    def test_audit_log_on_resolve(self):
        """action_resolve writes a resolved audit log."""
        exc = self._make_exception()
        exc.action_start_review()
        exc.action_resolve()

        resolve_log = exc.audit_log_ids.filtered(lambda l: l.action == "resolved")
        self.assertEqual(len(resolve_log), 1)
        self.assertEqual(resolve_log.old_state, "under_review")
        self.assertEqual(resolve_log.new_state, "resolved")

    def test_audit_log_on_waive(self):
        """action_waive writes a waived audit log."""
        exc = self._make_exception()
        exc.action_waive()

        waive_log = exc.audit_log_ids.filtered(lambda l: l.action == "waived")
        self.assertEqual(len(waive_log), 1)
        self.assertEqual(waive_log.new_state, "waived")

    def test_audit_log_on_escalate(self):
        """action_escalate writes an escalated audit log."""
        exc = self._make_exception()
        exc.action_start_review()
        exc.action_escalate()

        escalate_log = exc.audit_log_ids.filtered(lambda l: l.action == "escalated")
        self.assertEqual(len(escalate_log), 1)
        self.assertEqual(escalate_log.new_state, "escalated")

    def test_audit_log_on_reopen(self):
        """action_reopen writes a reopened audit log."""
        exc = self._make_exception()
        exc.action_resolve()
        exc.action_reopen()

        reopen_log = exc.audit_log_ids.filtered(lambda l: l.action == "reopened")
        self.assertEqual(len(reopen_log), 1)
        self.assertEqual(reopen_log.new_state, "detected")

    def test_audit_log_full_lifecycle_count(self):
        """Full lifecycle generates expected number of audit log entries."""
        exc = self._make_exception()
        exc.action_start_review()
        exc.action_resolve()
        exc.action_reopen()
        exc.action_waive()

        # created, review_started, resolved, reopened, waived = 5 entries
        self.assertEqual(len(exc.audit_log_ids), 5)

    def test_audit_log_has_user(self):
        """Audit log entries record the acting user."""
        exc = self._make_exception()
        for log in exc.audit_log_ids:
            self.assertTrue(log.user_id, "Audit log must record the user.")

    def test_audit_log_has_timestamp(self):
        """Audit log entries have a timestamp."""
        exc = self._make_exception()
        for log in exc.audit_log_ids:
            self.assertTrue(log.timestamp, "Audit log must have a timestamp.")

    def test_audit_log_count_computed(self):
        """audit_log_count field is correctly computed."""
        exc = self._make_exception()
        count_before = exc.audit_log_count
        exc.action_start_review()
        exc.audit_log_ids.invalidate_recordset()
        exc.invalidate_recordset(["audit_log_count"])
        count_after = exc.audit_log_count
        self.assertGreater(count_after, count_before)
