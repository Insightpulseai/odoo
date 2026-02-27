# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Boolean marker to identify the canonical TBWA\\SMP company.

Only one company should ever have ipai_is_tbwa_smp=True.  The record rule in
security/security.xml uses this flag as the domain for OMC-restricted users so
that non-sudo res.company searches return only the TBWA\\SMP company.
"""

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    ipai_is_tbwa_smp = fields.Boolean(
        string="Is TBWA\\SMP (OMC canonical company)",
        default=False,
        copy=False,
        help=(
            "Mark this company as the canonical TBWA\\SMP entity. "
            "OMC users (login ending @omc.com) will be restricted to this company only. "
            "Only one company should be marked True at a time."
        ),
    )

    @api.model
    def _ipai_mark_tbwa_smp_by_name(self, company_name):
        """Mark a company as the canonical TBWA\\SMP entity by exact name match.

        Called from data/company_marker.xml during module install/upgrade.
        Logs a warning (does NOT raise) if no company matches — so that module
        install succeeds even in environments where the company is named differently.
        Administrators should run scripts/company/mark_tbwa_smp_company.py manually
        in that case.

        Args:
            company_name (str): Exact company name to match.

        Returns:
            bool: True if the company was found and marked; False otherwise.
        """
        company = self.sudo().search([("name", "=", company_name)], limit=1)
        if not company:
            _logger.warning(
                "ipai_company_scope_omc: Company %r not found — "
                "ipai_is_tbwa_smp marker NOT set. "
                "Run scripts/company/mark_tbwa_smp_company.py to mark the correct company.",
                company_name,
            )
            return False
        if not company.ipai_is_tbwa_smp:
            company.sudo().write({"ipai_is_tbwa_smp": True})
            _logger.info(
                "ipai_company_scope_omc: Marked company %r (id=%d) as TBWA\\SMP.",
                company.name,
                company.id,
            )
        else:
            _logger.info(
                "ipai_company_scope_omc: Company %r (id=%d) is already marked as TBWA\\SMP.",
                company.name,
                company.id,
            )
        return True
