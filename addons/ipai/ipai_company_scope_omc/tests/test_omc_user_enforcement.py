# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Unit tests for @omc.com user company enforcement.

Covers:
  E1  create() — OMC user gets scoped to TBWA on create
  E2  create() — non-OMC user is NOT touched
  E3  write(login=) — switching login to @omc.com triggers scoping
  E4  write(company_id=) — reassigning company_id is immediately reversed
  E5  write(company_ids=) — expanding company_ids is immediately reversed
  E6  Idempotency — second enforcement call issues no write
  E7  Service/portal users (no @omc.com login) are never scoped
  E8  No TBWA company configured → enforcement raises ValidationError
"""

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


PARAM_KEY = "ipai.company.tbwa_company_id"


class TestOmcUserEnforcement(TransactionCase):

    def setUp(self):
        super().setUp()
        # Clear any existing param/flag
        self.env["ir.config_parameter"].sudo().set_param(PARAM_KEY, False)
        self.env["res.company"].sudo().search(
            [("ipai_is_tbwa_smp", "=", True)]
        ).write({"ipai_is_tbwa_smp": False})

        # Create the TBWA company and register it
        self.tbwa = self.env["res.company"].sudo().create(
            {"name": "TBWA SMP Test"}
        )
        self.tbwa.sudo().write({"ipai_is_tbwa_smp": True})
        self.env["ir.config_parameter"].sudo().set_param(
            PARAM_KEY, str(self.tbwa.id)
        )

        # Create a second company (the "wrong" one)
        self.other = self.env["res.company"].sudo().create(
            {"name": "Other Company Test"}
        )

    def tearDown(self):
        self.env["ir.config_parameter"].sudo().set_param(PARAM_KEY, False)
        self.env["res.company"].sudo().search(
            [("ipai_is_tbwa_smp", "=", True)]
        ).write({"ipai_is_tbwa_smp": False})
        super().tearDown()

    def _create_user(self, login, company_id=None):
        vals = {
            "name": f"Test {login}",
            "login": login,
            "groups_id": [(6, 0, [self.env.ref("base.group_user").id])],
        }
        if company_id:
            vals["company_id"] = company_id
        return self.env["res.users"].sudo().with_context(no_reset_password=True).create(vals)

    # ── Create enforcement ────────────────────────────────────────────────

    def test_E1_create_omc_user_scoped_to_tbwa(self):
        """E1: Creating @omc.com user results in company_id/company_ids = TBWA."""
        user = self._create_user("alice@omc.com", company_id=self.other.id)
        self.assertEqual(user.company_id.id, self.tbwa.id,
                         "company_id must be TBWA after create()")
        self.assertEqual(
            list(user.company_ids.ids), [self.tbwa.id],
            "company_ids must be [TBWA] only after create()"
        )

    def test_E2_create_non_omc_user_not_touched(self):
        """E2: Creating non-@omc.com user does not change their company."""
        user = self._create_user("bob@example.com", company_id=self.other.id)
        self.assertEqual(user.company_id.id, self.other.id,
                         "Non-OMC user's company must not be altered")

    # ── Write enforcement ─────────────────────────────────────────────────

    def test_E3_write_login_to_omc_triggers_scoping(self):
        """E3: Changing login to @omc.com immediately scopes the user."""
        user = self._create_user("carol@example.com", company_id=self.other.id)
        self.assertEqual(user.company_id.id, self.other.id)
        user.sudo().write({"login": "carol@omc.com"})
        self.assertEqual(user.company_id.id, self.tbwa.id)
        self.assertEqual(list(user.company_ids.ids), [self.tbwa.id])

    def test_E4_write_company_id_reversed_for_omc_user(self):
        """E4: Trying to reassign company_id for an OMC user is immediately reversed."""
        user = self._create_user("dave@omc.com")
        self.assertEqual(user.company_id.id, self.tbwa.id)
        # Attempt to move to other company
        user.sudo().write({"company_id": self.other.id})
        user.invalidate_recordset()
        self.assertEqual(user.company_id.id, self.tbwa.id,
                         "company_id must be restored to TBWA after write()")

    def test_E5_write_company_ids_reversed_for_omc_user(self):
        """E5: Trying to expand company_ids for an OMC user is immediately reversed."""
        user = self._create_user("eve@omc.com")
        # Attempt to grant access to both companies
        user.sudo().write({"company_ids": [(6, 0, [self.tbwa.id, self.other.id])]})
        user.invalidate_recordset()
        self.assertEqual(
            list(user.company_ids.ids), [self.tbwa.id],
            "company_ids must be [TBWA] only after write()"
        )

    # ── Idempotency ───────────────────────────────────────────────────────

    def test_E6_enforcement_is_idempotent(self):
        """E6: Calling _ipai_enforce_omc_scope() twice issues no extra writes."""
        user = self._create_user("frank@omc.com")
        # First enforcement (triggered by create) — already done
        self.assertEqual(user.company_id.id, self.tbwa.id)
        # Call again explicitly
        with self.assertQueryCount(0):
            user._ipai_enforce_omc_scope()

    # ── Non-OMC users are never scoped ───────────────────────────────────

    def test_E7_service_users_not_scoped(self):
        """E7: Users without @omc.com login are never scoped to TBWA."""
        user = self._create_user("service@internal.example", company_id=self.other.id)
        user.sudo().write({"company_id": self.other.id})
        self.assertEqual(user.company_id.id, self.other.id,
                         "Non-OMC user company must not be altered on write()")

    # ── Fail closed when no TBWA company configured ───────────────────────

    def test_E8_no_tbwa_company_raises_on_create(self):
        """E8: If resolver cannot find TBWA company, create() raises ValidationError."""
        # Remove param and flag
        self.env["ir.config_parameter"].sudo().set_param(PARAM_KEY, False)
        self.tbwa.sudo().write({"ipai_is_tbwa_smp": False})
        # Rename to remove 'TBWA' from name fallback
        self.tbwa.sudo().write({"name": "Renamed Company"})
        with self.assertRaises(ValidationError):
            self._create_user("grace@omc.com")
