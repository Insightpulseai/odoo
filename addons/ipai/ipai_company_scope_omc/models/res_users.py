# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Server-side enforcement: @omc.com users → TBWA\\SMP company only.

Uses ResCompany._ipai_tbwa_company() for deterministic resolution:
  1. ir.config_parameter ipai.company.tbwa_company_id  (preferred)
  2. Unique ipai_is_tbwa_smp=True flag
  3. Last-resort ilike "TBWA"

Enforcement fires on:
  - res.users.create()  — after the record exists
  - res.users.write()   — when login, company_id, or company_ids change

The companion record rule (security/security.xml) provides belt-and-suspenders
filtering so non-sudo searches on res.company return only TBWA\\SMP for
OMC-restricted users.
"""

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

OMC_DOMAIN = "@omc.com"

# Keys in vals that trigger re-enforcement on write()
_SCOPE_TRIGGER_KEYS = frozenset({"login", "company_id", "company_ids"})


class ResUsers(models.Model):
    _inherit = "res.users"

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _ipai_login_is_omc(login):
        """Return True if login ends with @omc.com (case-insensitive)."""
        return bool(login) and login.strip().lower().endswith(OMC_DOMAIN)

    def _ipai_enforce_omc_scope(self):
        """Hard-enforce company_id/company_ids = [TBWA\\SMP] for OMC users.

        Idempotent — if already correct, no write is issued.
        Called after create() and conditionally after write().

        Uses ResCompany._ipai_tbwa_company() for deterministic resolution.
        """
        # Resolve via the deterministic resolver on res.company
        tbwa = self.env["res.company"]._ipai_tbwa_company()

        for user in self:
            if not self._ipai_login_is_omc(user.login):
                continue

            # Idempotency check
            already_correct = (
                user.company_id.id == tbwa.id
                and set(user.company_ids.ids) == {tbwa.id}
            )
            if already_correct:
                continue

            _logger.info(
                "ipai_company_scope_omc: enforcing TBWA\\SMP scope for user %r "
                "(was company_id=%r, company_ids=%r)",
                user.login,
                user.company_id.name,
                user.company_ids.mapped("name"),
            )
            # Bypass our own write() override to avoid recursion
            super(ResUsers, user).write({
                "company_id": tbwa.id,
                "company_ids": [(6, 0, [tbwa.id])],
            })

    # ── ORM overrides ────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        for user, vals in zip(users, vals_list):
            if self._ipai_login_is_omc(vals.get("login", "")):
                user._ipai_enforce_omc_scope()
        return users

    def write(self, vals):
        res = super().write(vals)
        has_scope_change = bool(_SCOPE_TRIGGER_KEYS & vals.keys())
        for user in self:
            if has_scope_change or self._ipai_login_is_omc(user.login):
                user._ipai_enforce_omc_scope()
        return res
