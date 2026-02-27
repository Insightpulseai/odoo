# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Server-side enforcement: @omc.com users → TBWA\\SMP company only.

Enforcement runs on:
  - res.users.create()  — after the record exists
  - res.users.write()   — when login, company_id, or company_ids change

The companion record rule (security/security.xml) provides belt-and-suspenders
filtering so non-sudo res.company searches return only the marked company.

MRO notes:
  - No direct write() on self inside create() MRO; enforce is called after super()
  - _ipai_enforce_omc_scope() uses a targeted write that touches only
    company_id/company_ids — not the full record — to avoid recursion
"""

import logging

from odoo import api, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

OMC_DOMAIN = "@omc.com"

# Keys in vals that should trigger re-enforcement on write()
_SCOPE_TRIGGER_KEYS = frozenset({"login", "company_id", "company_ids"})


class ResUsers(models.Model):
    _inherit = "res.users"

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _ipai_tbwa_company(self):
        """Return the single TBWA\\SMP company (ipai_is_tbwa_smp=True).

        Raises ValidationError if none is marked — administrators must run
        scripts/company/mark_tbwa_smp_company.py once after module install.
        """
        company = (
            self.env["res.company"]
            .sudo()
            .search([("ipai_is_tbwa_smp", "=", True)], limit=1)
        )
        if not company:
            raise ValidationError(
                _(
                    "ipai_company_scope_omc: No company is marked as TBWA\\SMP "
                    "(ipai_is_tbwa_smp=True). "
                    "Run scripts/company/mark_tbwa_smp_company.py to mark the correct company."
                )
            )
        return company

    @staticmethod
    def _ipai_login_is_omc(login):
        """Return True if login ends with @omc.com (case-insensitive)."""
        return bool(login) and login.strip().lower().endswith(OMC_DOMAIN)

    def _ipai_enforce_omc_scope(self):
        """Hard-enforce company_id/company_ids = [TBWA\\SMP] for OMC users.

        Idempotent — if already correct, no write is issued.
        Called after create() and conditionally after write().
        """
        tbwa = self._ipai_tbwa_company()
        for user in self:
            if not self._ipai_login_is_omc(user.login):
                continue
            # Check current state to stay idempotent
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
            # Use super().write() to avoid re-triggering our override and
            # to skip the portal/public user guard in res.users.write()
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
        # Re-enforce if login or company fields changed, OR if any record is OMC
        has_scope_change = bool(_SCOPE_TRIGGER_KEYS & vals.keys())
        for user in self:
            if has_scope_change or self._ipai_login_is_omc(user.login):
                user._ipai_enforce_omc_scope()
        return res
