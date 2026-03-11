# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Unit tests for ResCompany._ipai_tbwa_company() resolver.

Covers all four resolution paths and their failure modes so regressions
(e.g. silently returning the wrong company) are caught in CI.

Test matrix:
  P1  param set + company exists              → returns that company
  P2  param set + company missing             → raises ValidationError
  P3  param set + bad (non-integer) value     → raises ValidationError
  F1  no param + exactly one flag             → returns flagged company
  F2  no param + multiple flags               → raises ValidationError (ambiguous)
  F3  no param + zero flags + TBWA-like name  → returns by name (warns)
  F4  no param + zero flags + no TBWA name    → raises ValidationError
"""

from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestTbwaCompanyResolver(TransactionCase):

    def setUp(self):
        super().setUp()
        # Ensure no stale param from previous test runs
        self._clear_param()
        # Ensure no stale flags
        self.env["res.company"].sudo().search(
            [("ipai_is_tbwa_smp", "=", True)]
        ).write({"ipai_is_tbwa_smp": False})

        # Create two isolated test companies
        self.company_a = self.env["res.company"].sudo().create(
            {"name": "Test Company Alpha (TBWA-like)"}
        )
        self.company_b = self.env["res.company"].sudo().create(
            {"name": "Test Company Beta"}
        )

    def tearDown(self):
        self._clear_param()
        # Unflag anything we set
        self.env["res.company"].sudo().search(
            [("ipai_is_tbwa_smp", "=", True)]
        ).write({"ipai_is_tbwa_smp": False})
        super().tearDown()

    def _clear_param(self):
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("ipai.company.tbwa_company_id", False)

    def _set_param(self, company_id):
        self.env["ir.config_parameter"].sudo().set_param(
            "ipai.company.tbwa_company_id", str(company_id)
        )

    # ── Param-based resolution ────────────────────────────────────────────

    def test_P1_param_set_valid_company(self):
        """P1: param set, company exists → returns that company."""
        self._set_param(self.company_a.id)
        result = self.env["res.company"]._ipai_tbwa_company()
        self.assertEqual(result.id, self.company_a.id)

    def test_P2_param_set_company_deleted(self):
        """P2: param set, company no longer exists → raises ValidationError."""
        self._set_param(self.company_a.id)
        # Simulate deletion by browsing a non-existent id
        self._set_param(999999999)
        with self.assertRaises(ValidationError):
            self.env["res.company"]._ipai_tbwa_company()

    def test_P3_param_set_non_integer(self):
        """P3: param holds a non-integer string → raises ValidationError."""
        self.env["ir.config_parameter"].sudo().set_param(
            "ipai.company.tbwa_company_id", "not-an-int"
        )
        with self.assertRaises(ValidationError):
            self.env["res.company"]._ipai_tbwa_company()

    # ── Flag-based resolution ─────────────────────────────────────────────

    def test_F1_no_param_exactly_one_flag(self):
        """F1: no param, exactly one company flagged → returns flagged company."""
        self.company_a.sudo().write({"ipai_is_tbwa_smp": True})
        result = self.env["res.company"]._ipai_tbwa_company()
        self.assertEqual(result.id, self.company_a.id)

    def test_F2_no_param_multiple_flags_raises(self):
        """F2: no param, multiple companies flagged → raises ValidationError (fail closed)."""
        self.company_a.sudo().write({"ipai_is_tbwa_smp": True})
        self.company_b.sudo().write({"ipai_is_tbwa_smp": True})
        with self.assertRaises(ValidationError) as cm:
            self.env["res.company"]._ipai_tbwa_company()
        self.assertIn("2 companies", str(cm.exception))

    def test_F2_error_message_lists_companies(self):
        """F2: ValidationError message names the ambiguous companies."""
        self.company_a.sudo().write({"ipai_is_tbwa_smp": True})
        self.company_b.sudo().write({"ipai_is_tbwa_smp": True})
        with self.assertRaises(ValidationError) as cm:
            self.env["res.company"]._ipai_tbwa_company()
        msg = str(cm.exception)
        # Both company ids should appear in the error
        self.assertIn(str(self.company_a.id), msg)
        self.assertIn(str(self.company_b.id), msg)

    # ── Name-fallback resolution ──────────────────────────────────────────

    def test_F3_no_param_no_flags_tbwa_name_returns_company(self):
        """F3: no param, no flags, company name contains 'TBWA' → returns it (with warning)."""
        # company_a is named "Test Company Alpha (TBWA-like)"
        with self.assertLogs("odoo.addons.ipai_company_scope_omc", level="WARNING"):
            result = self.env["res.company"]._ipai_tbwa_company()
        self.assertEqual(result.id, self.company_a.id)

    def test_F4_no_param_no_flags_no_tbwa_name_raises(self):
        """F4: no param, no flags, no company name matching 'TBWA' → raises ValidationError."""
        # Rename company_a to remove TBWA from name so no ilike match fires
        self.company_a.sudo().write({"name": "Test Company Alpha"})
        with self.assertRaises(ValidationError) as cm:
            self.env["res.company"]._ipai_tbwa_company()
        msg = str(cm.exception)
        self.assertIn("mark_tbwa_smp_company.py", msg)

    # ── Param takes priority over flag ───────────────────────────────────

    def test_param_priority_over_flag(self):
        """Param takes priority even when a different company has the flag set."""
        self.company_b.sudo().write({"ipai_is_tbwa_smp": True})
        self._set_param(self.company_a.id)  # param points to A, flag is on B
        result = self.env["res.company"]._ipai_tbwa_company()
        self.assertEqual(result.id, self.company_a.id,
                         "Param should take priority over flag")
