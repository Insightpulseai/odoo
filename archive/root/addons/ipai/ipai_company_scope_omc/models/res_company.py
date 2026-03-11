# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Boolean marker + deterministic resolver for the canonical TBWA\\SMP company.

Resolution order (most to least deterministic):
  1. ir.config_parameter "ipai.company.tbwa_company_id"  — set once by
     scripts/company/mark_tbwa_smp_company.py
  2. Unique boolean flag  ipai_is_tbwa_smp=True on res.company
  3. Last-resort name ilike "TBWA"  (first-install convenience only)

Fail-closed behaviour:
  - Param set   → company does not exist   → ValueError
  - Param unset → >1 company flagged       → ValueError (ambiguous)
  - Param unset → 0 flagged, no name match → ValueError (unresolvable)

Use scripts/company/mark_tbwa_smp_company.py once to set the param and
eliminate all ambiguity permanently.
"""

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# ir.config_parameter key — primary source of truth
PARAM_TBWA_COMPANY_ID = "ipai.company.tbwa_company_id"

# Human-readable message appended to every resolver failure
_INSTALL_HINT = (
    "Run scripts/company/mark_tbwa_smp_company.py "
    "(or set TBWA_COMPANY_ID=<id>) to make resolution deterministic."
)


class ResCompany(models.Model):
    _inherit = "res.company"

    ipai_is_tbwa_smp = fields.Boolean(
        string="Is TBWA\\SMP (OMC canonical company)",
        default=False,
        copy=False,
        help=(
            "Marks this company as the canonical TBWA\\SMP entity. "
            "OMC users (login ending @omc.com) are restricted to this company. "
            "Only one company should be marked True at a time. "
            "Prefer ir.config_parameter '%s' for deterministic resolution."
        ) % PARAM_TBWA_COMPANY_ID,
    )

    # ── Deterministic resolver ────────────────────────────────────────────

    @api.model
    def _ipai_tbwa_company(self):
        """Return the single canonical TBWA\\SMP company.  Fail closed.

        Resolution order:
          1. ir.config_parameter ipai.company.tbwa_company_id
          2. Unique ipai_is_tbwa_smp=True flag (fail if 0 or >1)
          3. Last-resort ilike "TBWA" name (warns; fail if nothing found)

        Raises:
            ValidationError: on any ambiguous or unresolvable state so that
                enforcement callers never silently scope to the wrong company.
        """
        # Step 1: config param — the only path that is unambiguous by design
        icp = self.env["ir.config_parameter"].sudo()
        param_val = icp.get_param(PARAM_TBWA_COMPANY_ID)
        if param_val:
            try:
                company_id = int(param_val)
            except (ValueError, TypeError):
                raise ValidationError(
                    "ipai_company_scope_omc: %r = %r is not a valid integer. "
                    "%s" % (PARAM_TBWA_COMPANY_ID, param_val, _INSTALL_HINT)
                )
            company = self.sudo().browse(company_id)
            if not company.exists():
                raise ValidationError(
                    "ipai_company_scope_omc: %r = %d but that company no longer "
                    "exists. %s" % (PARAM_TBWA_COMPANY_ID, company_id, _INSTALL_HINT)
                )
            return company

        # Step 2: unique flag — fail closed on ambiguity
        flagged = self.sudo().search([("ipai_is_tbwa_smp", "=", True)])
        if len(flagged) == 1:
            _logger.info(
                "ipai_company_scope_omc: resolved via ipai_is_tbwa_smp flag "
                "(id=%d name=%r). Set %r for deterministic resolution.",
                flagged.id, flagged.name, PARAM_TBWA_COMPANY_ID,
            )
            return flagged
        if len(flagged) > 1:
            raise ValidationError(
                "ipai_company_scope_omc: %d companies have ipai_is_tbwa_smp=True "
                "(%s). Exactly one must be marked. %s"
                % (
                    len(flagged),
                    ", ".join("id=%d name=%r" % (c.id, c.name) for c in flagged),
                    _INSTALL_HINT,
                )
            )

        # Step 3: last-resort name match — convenience only, warns loudly
        by_name = self.sudo().search([("name", "ilike", "TBWA")], limit=1)
        if by_name:
            _logger.warning(
                "ipai_company_scope_omc: resolved TBWA company by name fallback "
                "(id=%d name=%r). This is only safe if there is no other company "
                "with 'TBWA' in the name. %s",
                by_name.id, by_name.name, _INSTALL_HINT,
            )
            return by_name

        # Nothing found — fail closed
        raise ValidationError(
            "ipai_company_scope_omc: Cannot resolve TBWA\\SMP company. "
            "No config param, no flagged company, no company name containing "
            "'TBWA'. %s" % _INSTALL_HINT
        )

    # ── Install-time convenience helper (called from data XML) ───────────

    @api.model
    def _ipai_mark_tbwa_smp_by_name(self, company_name):
        """Convenience-only: mark a company by exact name at module install.

        Called from data/company_marker.xml.  Logs WARNING (does NOT raise)
        if the company is not found — module install succeeds regardless.
        The deterministic path for all environments is
        scripts/company/mark_tbwa_smp_company.py.
        """
        company = self.sudo().search([("name", "=", company_name)], limit=1)
        if not company:
            _logger.warning(
                "ipai_company_scope_omc: Company %r not found at install time. "
                "ipai_is_tbwa_smp NOT set automatically. %s",
                company_name, _INSTALL_HINT,
            )
            return False
        if not company.ipai_is_tbwa_smp:
            company.sudo().write({"ipai_is_tbwa_smp": True})
            _logger.info(
                "ipai_company_scope_omc: Marked company %r (id=%d) as TBWA\\SMP "
                "via install-time name match.",
                company.name, company.id,
            )
        return True
