# -*- coding: utf-8 -*-
from odoo import fields, models


class HrExpenseCashAdvanceLink(models.Model):
    _inherit = "hr.expense"

    cash_advance_liquidation_id = fields.Many2one(
        "hr.expense.liquidation",
        string="Cash Advance Liquidation",
        domain=[("liquidation_type", "=", "cash_advance")],
        ondelete="set null",
        index=True,
    )
    cash_advance_form_no = fields.Char(
        string="Liquidation Form No.",
        related="cash_advance_liquidation_id.name",
        store=True,
        readonly=True,
    )
