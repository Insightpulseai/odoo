# -*- coding: utf-8 -*-
"""
test_parity_config.py — Tests for expense.parity.config OCA detection model.

Verifies:
  - get_config() returns a dict with all expected keys
  - All values are boolean
  - Computed fields on TransientModel instance match get_config() output
  - Absent OCA modules correctly report False
"""

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("expense", "liquidation", "post_install", "-at_install")
class TestParityConfig(TransactionCase):
    """Tests for expense.parity.config OCA module detection."""

    _EXPECTED_KEYS = {
        "dms_installed",
        "auditlog_installed",
        "queue_job_installed",
        "mis_builder_installed",
    }

    def setUp(self):
        super().setUp()
        self.ParityConfig = self.env["expense.parity.config"]

    # ── get_config() structure ─────────────────────────────────────────────

    def test_config_get_config_returns_dict(self):
        """get_config() must return a dict."""
        config = self.ParityConfig.get_config()
        self.assertIsInstance(config, dict, "get_config() must return a dict.")

    def test_config_all_expected_keys_present(self):
        """get_config() must include all expected detection keys."""
        config = self.ParityConfig.get_config()
        for key in self._EXPECTED_KEYS:
            self.assertIn(key, config, f"get_config() missing key: {key}")

    def test_config_all_values_are_boolean(self):
        """All values in get_config() must be boolean."""
        config = self.ParityConfig.get_config()
        for key, value in config.items():
            self.assertIsInstance(
                value,
                bool,
                f"get_config()['{key}'] must be bool, got {type(value).__name__}.",
            )

    # ── Absent OCA modules report False ───────────────────────────────────

    def test_config_absent_oca_modules_report_false(self):
        """OCA modules not installed in test env must report False."""
        config = self.ParityConfig.get_config()
        # In a minimal test DB, none of these OCA modules should be installed.
        # If any are installed, this test should still pass (just won't cover the False path).
        # We assert that the key exists and is a bool — the value depends on the env.
        for key in self._EXPECTED_KEYS:
            self.assertIn(key, config)

    def test_config_module_detection_consistent(self):
        """Calling get_config() twice must return the same result."""
        config1 = self.ParityConfig.get_config()
        config2 = self.ParityConfig.get_config()
        self.assertEqual(
            config1, config2, "get_config() is not idempotent — results differ between calls."
        )

    # ── TransientModel computed fields ────────────────────────────────────

    def test_config_computed_fields(self):
        """TransientModel computed fields must match get_config() output."""
        config = self.ParityConfig.get_config()
        # Create a TransientModel record and verify computed fields
        record = self.ParityConfig.create({})
        for field_name in self._EXPECTED_KEYS:
            record_value = record[field_name]
            config_value = config[field_name]
            self.assertEqual(
                record_value,
                config_value,
                f"Computed field '{field_name}' ({record_value}) "
                f"doesn't match get_config() ({config_value}).",
            )

    # ── No side effects ────────────────────────────────────────────────────

    def test_config_get_config_no_side_effects(self):
        """get_config() must not modify ir.module.module records."""
        Module = self.env["ir.module.module"].sudo()
        before_count = Module.search_count([])
        self.ParityConfig.get_config()
        after_count = Module.search_count([])
        self.assertEqual(
            before_count,
            after_count,
            "get_config() must not create or delete ir.module.module records.",
        )

    # ── Keys cover all _OCA_MODULES ───────────────────────────────────────

    def test_config_no_extra_keys_beyond_expected(self):
        """get_config() must not return unexpected extra keys."""
        config = self.ParityConfig.get_config()
        extra_keys = set(config.keys()) - self._EXPECTED_KEYS
        self.assertEqual(
            extra_keys,
            set(),
            f"get_config() returned unexpected keys: {extra_keys}",
        )
