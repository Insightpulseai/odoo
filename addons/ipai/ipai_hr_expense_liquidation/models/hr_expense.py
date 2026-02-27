# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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

    @api.constrains("cash_advance_liquidation_id", "employee_id", "company_id")
    def _check_advance_scope_match(self):
        """
        An expense's employee and company must match the linked liquidation's
        to prevent cross-entity reconciliation errors.
        """
        for expense in self:
            liq = expense.cash_advance_liquidation_id
            if not liq:
                continue
            if expense.employee_id != liq.employee_id:
                raise ValidationError(_(
                    "Expense '%s': employee (%s) does not match "
                    "liquidation %s employee (%s)."
                ) % (
                    expense.name,
                    expense.employee_id.name,
                    liq.name,
                    liq.employee_id.name,
                ))
            if expense.company_id != liq.company_id:
                raise ValidationError(_(
                    "Expense '%s': company (%s) does not match "
                    "liquidation %s company (%s)."
                ) % (
                    expense.name,
                    expense.company_id.name,
                    liq.name,
                    liq.company_id.name,
                ))
