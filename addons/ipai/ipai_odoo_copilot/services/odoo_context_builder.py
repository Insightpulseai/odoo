# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class OdooContextBuilder(models.AbstractModel):
    """Build normalized context payloads for Diva Goals agents.

    Extracts record, company, user, and tax context from the current
    Odoo environment. Output is a plain dict — no Odoo recordsets cross
    the boundary.
    """

    _name = 'ipai.copilot.context.builder'
    _description = 'Odoo Context Builder for Agent Payloads'

    @api.model
    def build_user_context(self):
        """Current user identity and permissions."""
        user = self.env.user
        return {
            'user_id': user.id,
            'user_name': user.name,
            'user_login': user.login,
            'company_id': user.company_id.id,
            'company_name': user.company_id.name,
            'groups': user.group_ids.mapped('full_name'),
            'lang': user.lang or 'en_US',
            'tz': user.tz or 'Asia/Manila',
        }

    @api.model
    def build_company_context(self, company=None):
        """Company-level context for tax and finance operations."""
        company = company or self.env.company
        return {
            'company_id': company.id,
            'company_name': company.name,
            'currency': company.currency_id.name,
            'country_code': company.country_id.code or 'PH',
            'vat': company.vat or '',
            'fiscal_year_last_month': company.fiscalyear_last_month,
        }

    @api.model
    def build_record_context(self, record):
        """Minimal record context for a single Odoo record."""
        if not record:
            return {}
        return {
            'model': record._name,
            'res_id': record.id,
            'display_name': record.display_name,
            'create_date': str(record.create_date) if record.create_date else None,
            'write_date': str(record.write_date) if record.write_date else None,
        }

    @api.model
    def build_tax_context(self):
        """Philippine tax context for BIR-related operations."""
        company = self.env.company
        ICP = self.env['ir.config_parameter'].sudo()
        return {
            'country_code': company.country_id.code or 'PH',
            'vat_registered': bool(company.vat),
            'tin': ICP.get_param('ipai_bir.company_tin', default=''),
            'rdo_code': ICP.get_param('ipai_bir.rdo_code', default=''),
            'bir_category': ICP.get_param('ipai_bir.taxpayer_category', default=''),
        }

    @api.model
    def build_full_context(self, record=None, include_tax=False):
        """Assemble full context payload for Diva backend."""
        ctx = {
            'user': self.build_user_context(),
            'company': self.build_company_context(),
        }
        if record:
            ctx['record'] = self.build_record_context(record)
        if include_tax:
            ctx['tax'] = self.build_tax_context()
        return ctx
