# -*- coding: utf-8 -*-
"""
test_expense_wiring.py — Tests for hr.expense.sheet wiring additions.

Verifies:
  - receipt_archive_ref field exists on hr.expense.sheet
  - action_archive_receipts() returns correct structure
  - Graceful no-op when dms is absent
  - DMS detection reflected in result dict
"""

from unittest.mock import patch, MagicMock

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("expense", "liquidation", "post_install", "-at_install")
class TestExpenseWiring(TransactionCase):
    """Tests for hr.expense.sheet wiring additions (dms, auditlog, queue_job detection)."""

    def setUp(self):
        super().setUp()
        # Create a minimal employee to avoid demo data dependency
        self.employee = self.env["hr.employee"].create(
            {"name": "Test Wiring Employee"}
        )
        # Use a simple expense product — create one to avoid demo data dependency
        self.product = self.env["product.product"].create(
            {
                "name": "Test Expense Product",
                "type": "service",
                "can_be_expensed": True,
            }
        )
        self.expense = self.env["hr.expense"].create(
            {
                "name": "Test Expense",
                "employee_id": self.employee.id,
                "product_id": self.product.id,
                "total_amount": 100.0,
            }
        )
        self.sheet = self.env["hr.expense.sheet"].create(
            {
                "name": "Test Expense Sheet",
                "employee_id": self.employee.id,
                "expense_line_ids": [(4, self.expense.id)],
            }
        )

    # ── Field presence ─────────────────────────────────────────────────────

    def test_receipt_archive_ref_field_exists(self):
        """receipt_archive_ref field must exist on hr.expense.sheet."""
        self.assertIn(
            "receipt_archive_ref",
            self.env["hr.expense.sheet"]._fields,
            "receipt_archive_ref field missing from hr.expense.sheet.",
        )

    def test_receipt_archive_ref_initially_empty(self):
        """receipt_archive_ref must be empty on a new expense sheet."""
        self.assertFalse(
            self.sheet.receipt_archive_ref,
            "receipt_archive_ref must be empty on new sheet.",
        )

    # ── action_archive_receipts() when dms absent ─────────────────────────

    def test_receipt_archive_when_dms_absent(self):
        """action_archive_receipts must return graceful no-op result when dms not installed."""
        # Patch get_config to return dms_installed=False
        with patch.object(
            type(self.env["expense.parity.config"]),
            "get_config",
            return_value={
                "dms_installed": False,
                "auditlog_installed": False,
                "queue_job_installed": False,
                "mis_builder_installed": False,
            },
        ):
            result = self.sheet.action_archive_receipts()

        self.assertIsInstance(result, dict, "action_archive_receipts must return a dict.")
        self.assertFalse(result["dms_available"], "dms_available must be False when dms absent.")
        self.assertEqual(result["archived_count"], 0, "archived_count must be 0 when dms absent.")
        self.assertTrue(result["skipped"], "skipped must be True when dms absent.")
        self.assertIn("message", result, "Result must include a message key.")

    def test_receipt_archive_ref_not_set_when_dms_absent(self):
        """receipt_archive_ref must remain empty when dms is absent."""
        with patch.object(
            type(self.env["expense.parity.config"]),
            "get_config",
            return_value={
                "dms_installed": False,
                "auditlog_installed": False,
                "queue_job_installed": False,
                "mis_builder_installed": False,
            },
        ):
            self.sheet.action_archive_receipts()

        self.assertFalse(
            self.sheet.receipt_archive_ref,
            "receipt_archive_ref must remain empty when dms is absent.",
        )

    # ── action_archive_receipts() when dms present ────────────────────────

    def test_receipt_archive_when_dms_present(self):
        """action_archive_receipts must return dms_available=True and set archive_ref."""
        with patch.object(
            type(self.env["expense.parity.config"]),
            "get_config",
            return_value={
                "dms_installed": True,
                "auditlog_installed": False,
                "queue_job_installed": False,
                "mis_builder_installed": False,
            },
        ):
            result = self.sheet.action_archive_receipts()

        self.assertTrue(result["dms_available"], "dms_available must be True when dms is installed.")
        self.assertFalse(result["skipped"], "skipped must be False when dms is installed.")
        self.assertIn("message", result)

    def test_receipt_archive_ref_set_when_dms_present(self):
        """receipt_archive_ref must be set on the sheet when dms is installed."""
        with patch.object(
            type(self.env["expense.parity.config"]),
            "get_config",
            return_value={
                "dms_installed": True,
                "auditlog_installed": False,
                "queue_job_installed": False,
                "mis_builder_installed": False,
            },
        ):
            self.sheet.action_archive_receipts()

        self.assertTrue(
            self.sheet.receipt_archive_ref,
            "receipt_archive_ref must be set when dms is installed.",
        )
        self.assertIn(
            str(self.sheet.id),
            self.sheet.receipt_archive_ref,
            "receipt_archive_ref must contain the sheet ID.",
        )

    # ── DMS detection reflected in result ─────────────────────────────────

    def test_dms_detection_result_structure(self):
        """Result dict must always contain all required keys regardless of dms state."""
        required_keys = {"dms_available", "archived_count", "skipped", "message"}
        for dms_state in (True, False):
            with patch.object(
                type(self.env["expense.parity.config"]),
                "get_config",
                return_value={
                    "dms_installed": dms_state,
                    "auditlog_installed": False,
                    "queue_job_installed": False,
                    "mis_builder_installed": False,
                },
            ):
                result = self.sheet.action_archive_receipts()
            self.assertEqual(
                set(result.keys()),
                required_keys,
                f"Result dict missing keys when dms_installed={dms_state}.",
            )

    # ── auditlog detection ─────────────────────────────────────────────────

    def test_auditlog_detection(self):
        """get_config must report auditlog_installed correctly."""
        config = self.env["expense.parity.config"].get_config()
        # auditlog module is not expected in test env — should be False
        self.assertIn("auditlog_installed", config, "auditlog_installed key missing from config.")
        self.assertIsInstance(config["auditlog_installed"], bool)
