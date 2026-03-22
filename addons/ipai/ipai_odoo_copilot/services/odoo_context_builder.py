import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class OdooContextBuilder:
    """Build structured context dicts from Odoo records.

    Every method accepts an Odoo ``env`` object (or record) and returns
    a plain dict suitable for serialisation to JSON.  No external calls
    are made — all data comes from the ORM.
    """

    # ------------------------------------------------------------------
    # Record context
    # ------------------------------------------------------------------

    @staticmethod
    def build_record_context(env, model: str, record_id: int) -> dict:
        """Build context from an arbitrary Odoo record.

        Args:
            env: Odoo environment (``self.env`` from a model method).
            model: Technical model name (e.g. ``"account.move"``).
            record_id: Database id of the target record.

        Returns:
            Dict with model, id, display_name, state (if present),
            and write_date.
        """
        record = env[model].browse(record_id)
        if not record.exists():
            _logger.warning(
                'build_record_context: %s(%s) does not exist', model, record_id,
            )
            return {'model': model, 'id': record_id, 'exists': False}

        ctx = {
            'model': model,
            'id': record_id,
            'exists': True,
            'display_name': record.display_name,
            'write_date': record.write_date.isoformat() if record.write_date else None,
        }
        if hasattr(record, 'state'):
            ctx['state'] = record.state
        return ctx

    # ------------------------------------------------------------------
    # Company context
    # ------------------------------------------------------------------

    @staticmethod
    def build_company_context(env) -> dict:
        """Build company / tenant context from the current environment.

        Returns:
            Dict with company id, name, currency, country code, and
            fiscal year lock date (if set).
        """
        company = env.company
        ctx = {
            'company_id': company.id,
            'company_name': company.name,
            'currency': company.currency_id.name if company.currency_id else None,
            'country_code': company.country_id.code if company.country_id else None,
        }
        if hasattr(company, 'fiscalyear_lock_date'):
            lock = company.fiscalyear_lock_date
            ctx['fiscalyear_lock_date'] = lock.isoformat() if lock else None
        return ctx

    # ------------------------------------------------------------------
    # User context
    # ------------------------------------------------------------------

    @staticmethod
    def build_user_context(env) -> dict:
        """Build user identity context from the current environment.

        Returns:
            Dict with uid, login, name, timezone, lang, and group
            XML-IDs.
        """
        user = env.user
        groups = user.group_ids.mapped(
            lambda g: g.get_external_id().get(g.id, '')
        ) if user.group_ids else []
        return {
            'uid': user.id,
            'login': user.login,
            'name': user.name,
            'tz': user.tz or 'UTC',
            'lang': user.lang or 'en_US',
            'groups': [g for g in groups if g],
        }

    # ------------------------------------------------------------------
    # Tax context (account.move)
    # ------------------------------------------------------------------

    @staticmethod
    def build_tax_context(env, move_id: int) -> dict:
        """Build tax-specific context from an ``account.move``.

        Designed for Philippine BIR compliance workflows — extracts
        partner TIN, tax lines, withholding amounts, and move metadata.

        Args:
            env: Odoo environment.
            move_id: Database id of the ``account.move`` record.

        Returns:
            Dict with move metadata, partner TIN, and tax line
            summaries.
        """
        move = env['account.move'].browse(move_id)
        if not move.exists():
            _logger.warning(
                'build_tax_context: account.move(%s) does not exist', move_id,
            )
            return {'move_id': move_id, 'exists': False}

        tax_lines = []
        for line in move.line_ids.filtered(lambda l: l.tax_line_id):
            tax_lines.append({
                'tax_name': line.tax_line_id.name,
                'tax_amount': line.balance,
                'account': line.account_id.code if line.account_id else None,
            })

        partner = move.partner_id
        return {
            'move_id': move_id,
            'exists': True,
            'move_name': move.name,
            'move_type': move.move_type,
            'state': move.state,
            'date': move.date.isoformat() if move.date else None,
            'amount_total': move.amount_total,
            'currency': move.currency_id.name if move.currency_id else None,
            'partner_name': partner.name if partner else None,
            'partner_vat': partner.vat if partner else None,
            'tax_lines': tax_lines,
        }
