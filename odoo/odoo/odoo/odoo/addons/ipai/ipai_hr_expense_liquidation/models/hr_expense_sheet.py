# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import ValidationError


class HrExpenseSheetCAConstraint(models.Model):
    _inherit = "hr.expense.sheet"

    @api.constrains("expense_line_ids")
    def _check_single_cash_advance_per_sheet(self):
        for sheet in self:
            liq_ids = sheet.expense_line_ids.mapped(
                "cash_advance_liquidation_id"
            ).filtered(bool)
            if len(liq_ids) > 1:
                raise ValidationError(_(
                    "All expense lines must reference the same Cash Advance "
                    "Liquidation form. Found: %s"
                ) % ", ".join(liq_ids.mapped("name")))
