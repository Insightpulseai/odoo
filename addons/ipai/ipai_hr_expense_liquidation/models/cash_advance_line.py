# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CashAdvanceLine(models.Model):
    """Individual purpose/breakdown line for a Cash Advance request."""

    _name = "cash.advance.line"
    _description = "Cash Advance Purpose Line"
    _order = "id"

    cash_advance_id = fields.Many2one(
        "cash.advance",
        string="Cash Advance",
        required=True,
        ondelete="cascade",
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="cash_advance_id.currency_id",
        store=True,
    )

    purpose = fields.Char(string="Purpose", required=True)
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        required=True,
    )
