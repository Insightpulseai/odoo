# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Boolean marker + deterministic resolver for the canonical TBWA\\SMP company.

Resolution order (most to least deterministic):
  1. ir.config_parameter "ipai.company.tbwa_company_id"  — set once by
     scripts/company/mark_tbwa_smp_company.py; never needs to be touched again
  2. Unique boolean flag  ipai_is_tbwa_smp=True on res.company
  3. Last-resort name ilike "TBWA" (legacy / first-install fallback)

This order means:
  - Adding a new company named "TBWA Anything" will NOT break enforcement as
    long as the config param is set.
  - If config param is not set but exactly one company is flagged, that is used.
  - The name fallback only triggers when neither of the above exists.
"""

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# ir.config_parameter key — set by mark_tbwa_smp_company.py
PARAM_TBWA_COMPANY_ID = "ipai.company.tbwa_company_id"


class ResCompany(models.Model):
    _inherit = "res.company"

    ipai_is_tbwa_smp = fields.Boolean(
        string="Is TBWA\\SMP (OMC canonical company)",
        default=False,
        copy=False,
        help=(
            "Mark this company as the canonical TBWA\\SMP entity. "
            "OMC users (login ending @omc.com) are restricted to this company. "
            "Only one company should be marked True at a time. "
            "Prefer setting ir.config_parameter 'ipai.company.tbwa_company_id' "
            "via scripts/company/mark_tbwa_smp_company.py for deterministic resolution."
        ),
    )

    # ── Deterministic resolver ────────────────────────────────────────────

    @api.model
    def _ipai_tbwa_company(self):
        """Return the single canonical TBWA\\SMP company.

        Resolution order:
          1. ir.config_parameter ipai.company.tbwa_company_id
          2. Unique ipai_is_tbwa_smp=True flag
          3. Last-resort: ilike "TBWA" (warns, for first-install convenience)

        Raises ValidationError if no company can be resolved — admin must run
        scripts/company/mark_tbwa_smp_company.py.
        """
        # Step 1: config param (most deterministic)
        icp = self.env["ir.config_parameter"].sudo()
        param_val = icp.get_param(PARAM_TBWA_COMPANY_ID)
        if param_val:
            try:
                company = self.sudo().browse(int(param_val))
                if company.exists():
                    return company
                _logger.warning(
                    "ipai_company_scope_omc: %r = %r but company id=%s does not exist. "
                    "Falling back to flag/name resolution.",
                    PARAM_TBWA_COMPANY_ID, param_val, param_val,
                )
            except (ValueError, TypeError):
                _logger.warning(
                    "ipai_company_scope_omc: %r = %r is not a valid integer. "
                    "Falling back.",
                    PARAM_TBWA_COMPANY_ID, param_val,
                )

        # Step 2: unique flag
        flagged = self.sudo().search([("ipai_is_tbwa_smp", "=", True)], limit=2)
        if len(flagged) == 1:
            return flagged
        if len(flagged) > 1:
            _logger.warning(
                "ipai_company_scope_omc: %d companies have ipai_is_tbwa_smp=True. "
                "Only one should be marked. Using id=%d name=%r.",
                len(flagged), flagged[0].id, flagged[0].name,
            )
            return flagged[0]

        # Step 3: name fallback (last resort, first-install only)
        by_name = self.sudo().search([("name", "ilike", "TBWA")], limit=1)
        if by_name:
            _logger.warning(
                "ipai_company_scope_omc: resolved TBWA company by name fallback "
                "(id=%d name=%r). Run scripts/company/mark_tbwa_smp_company.py "
                "to make resolution deterministic.",
                by_name.id, by_name.name,
            )
            return by_name

        raise ValidationError(
            "ipai_company_scope_omc: Cannot resolve TBWA\\SMP company. "
            "Run scripts/company/mark_tbwa_smp_company.py to mark the correct company "
            "and set ir.config_parameter '%s'." % PARAM_TBWA_COMPANY_ID
        )

    # ── Install-time helper (called from data XML via <function>) ─────────

    @api.model
    def _ipai_mark_tbwa_smp_by_name(self, company_name):
        """Mark a company as the canonical TBWA\\SMP entity by exact name match.

        Called from data/company_marker.xml during module install/upgrade ONLY
        as a convenience for environments where the company IS named exactly
        'TBWA\\SMP'. Logs WARNING and returns False (no error) if not found —
        module install succeeds regardless.

        For all other environments, use mark_tbwa_smp_company.py which also
        sets ir.config_parameter ipai.company.tbwa_company_id.
        """
        company = self.sudo().search([("name", "=", company_name)], limit=1)
        if not company:
            _logger.warning(
                "ipai_company_scope_omc: Company %r not found at install time. "
                "ipai_is_tbwa_smp NOT set automatically. "
                "Run scripts/company/mark_tbwa_smp_company.py to mark the correct company.",
                company_name,
            )
            return False
        if not company.ipai_is_tbwa_smp:
            company.sudo().write({"ipai_is_tbwa_smp": True})
            _logger.info(
                "ipai_company_scope_omc: Marked company %r (id=%d) as TBWA\\SMP.",
                company.name, company.id,
            )
        return True
