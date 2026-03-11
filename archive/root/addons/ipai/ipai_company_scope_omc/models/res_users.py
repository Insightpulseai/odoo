# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Server-side enforcement: @omc.com users → TBWA\\SMP company only.

Enforcement rules:
  - Only fires for users whose `login` is set and ends with "@omc.com".
  - Uses ResCompany._ipai_tbwa_company() which fails closed on ambiguity.
  - Idempotent: no write issued if company_id/company_ids are already correct.
  - Does NOT fire for internal/system users (login == '__system__' etc.).

Hooks:
  - create()  — after the record exists (login is stable)
  - write()   — only when login, company_id, or company_ids change
                (avoids touching unrelated writes on non-OMC users)
"""

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

OMC_DOMAIN = "@omc.com"

# Only re-enforce on write() when these keys appear in vals
_SCOPE_TRIGGER_KEYS = frozenset({"login", "company_id", "company_ids"})


class ResUsers(models.Model):
    _inherit = "res.users"

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _ipai_login_is_omc(login):
        """Return True iff login is a non-empty string ending with @omc.com."""
        return isinstance(login, str) and bool(login) and login.strip().lower().endswith(OMC_DOMAIN)

    def _ipai_enforce_omc_scope(self):
        """Hard-enforce company_id/company_ids = [TBWA\\SMP] for OMC users.

        Idempotent: if the record is already correctly scoped, no write occurs.
        Calls ResCompany._ipai_tbwa_company() which raises ValidationError on
        any ambiguous or unresolvable state (fail closed).
        """
        # Filter to OMC users only — avoids unnecessary resolver calls
        omc_users = self.filtered(
            lambda u: self._ipai_login_is_omc(u.login)
        )
        if not omc_users:
            return

        # Resolve once for the whole batch
        tbwa = self.env["res.company"]._ipai_tbwa_company()

        for user in omc_users:
            already_correct = (
                user.company_id.id == tbwa.id
                and set(user.company_ids.ids) == {tbwa.id}
            )
            if already_correct:
                continue

            _logger.info(
                "ipai_company_scope_omc: enforcing TBWA\\SMP scope for user %r "
                "(company_id=%r → %r, company_ids=%r → [%r])",
                user.login,
                user.company_id.name, tbwa.name,
                user.company_ids.mapped("name"), tbwa.name,
            )
            # Bypass our own write() to avoid recursion
            super(ResUsers, user).write({
                "company_id": tbwa.id,
                "company_ids": [(6, 0, [tbwa.id])],
            })

    # ── ORM overrides ────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        # Gate: only enforce when login was provided and is @omc.com.
        # login is stable after create() has returned.
        for user, vals in zip(users, vals_list):
            if self._ipai_login_is_omc(vals.get("login", "")):
                user._ipai_enforce_omc_scope()
        return users

    def write(self, vals):
        res = super().write(vals)
        # Gate: only enforce when scope-relevant keys are being written,
        # OR when iterating over records that are already @omc.com users.
        # This avoids touching unrelated writes (e.g. updating name/email).
        vals_has_scope_key = bool(_SCOPE_TRIGGER_KEYS & vals.keys())
        if vals_has_scope_key:
            # May have changed login or company — check all records in self
            self._ipai_enforce_omc_scope()
        else:
            # vals has no scope key but some records in self may be OMC users
            # whose company got reset externally — only enforce those
            self.filtered(
                lambda u: self._ipai_login_is_omc(u.login)
            )._ipai_enforce_omc_scope()
        return res
