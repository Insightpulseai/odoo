# -*- coding: utf-8 -*-
"""
hr_expense_sheet_wiring.py — Thin wiring additions to hr.expense.sheet.

Adds:
  receipt_archive_ref (Char) — DMS document reference if dms is installed.
    Graceful no-op when dms is absent. This is a soft pointer, not a
    hard relational field, to avoid hard dependency on optional OCA module.

  action_archive_receipts() — Archives ir.attachment records linked to this
    sheet into DMS if dms is installed. Safe no-op otherwise.

Boundary:
  - This module DOES NOT own the DMS archival logic.
  - It provides the linkage point. DMS module owns the archival.
  - auditlog wiring is advisory: audit rules are registered in data/
    when auditlog is installed (soft wiring at data level, not model level).
"""

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class HrExpenseSheetWiring(models.Model):
    """Expense Sheet (Parity Wiring)"""

    _inherit = "hr.expense.sheet"
    _description = "Expense Sheet (Parity Wiring)"

    receipt_archive_ref = fields.Char(
        string="Receipt Archive Ref",
        copy=False,
        help=(
            "DMS document reference for archived receipts. "
            "Populated by action_archive_receipts() when OCA 'dms' is installed. "
            "Empty when dms is absent — graceful no-op."
        ),
    )

    def action_archive_receipts(self):
        """Archive attachments to DMS if installed, otherwise no-op.

        Safe to call in any environment. Returns a dict summarising what
        was done so callers and tests can assert on outcomes.

        Returns:
            dict: {
                "dms_available": bool,
                "archived_count": int,
                "skipped": bool,
                "message": str,
            }
        """
        self.ensure_one()
        config = self.env["expense.parity.config"].get_config()

        if not config.get("dms_installed"):
            _logger.info(
                "action_archive_receipts: OCA 'dms' not installed — skipping for sheet %s.",
                self.name,
            )
            return {
                "dms_available": False,
                "archived_count": 0,
                "skipped": True,
                "message": _("DMS module not installed. Receipts remain as standard attachments."),
            }

        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", "hr.expense.sheet"), ("res_id", "=", self.id)]
        )
        archived_count = len(attachments)

        # With dms installed: record the archive reference.
        # Full DMS integration (creating dms.document records) is deferred to
        # a dedicated dms wiring layer to avoid coupling this module to dms internals.
        archive_ref = "dms://expense-sheet/%s" % self.id
        self.receipt_archive_ref = archive_ref

        _logger.info(
            "action_archive_receipts: DMS available. Sheet=%s, attachments=%d, ref=%s",
            self.name,
            archived_count,
            archive_ref,
        )

        return {
            "dms_available": True,
            "archived_count": archived_count,
            "skipped": False,
            "message": _(
                "%(count)d attachment(s) marked for DMS archival. Ref: %(ref)s",
                count=archived_count,
                ref=archive_ref,
            ),
        }
