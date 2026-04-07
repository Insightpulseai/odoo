from odoo import api, fields, models
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    """Extend hr.expense.sheet with compliance exception tracking
    and blocking-exception gate on approval."""

    _inherit = "hr.expense.sheet"

    exception_ids = fields.One2many(
        "ipai.expense.exception", "sheet_id", string="Exceptions",
    )

    exception_count = fields.Integer(
        compute="_compute_exception_count",
    )
    blocking_exception_count = fields.Integer(
        compute="_compute_exception_count",
    )

    @api.depends("exception_ids.state", "exception_ids.is_blocking")
    def _compute_exception_count(self):
        for rec in self:
            active = rec.exception_ids.filtered(lambda e: e.state in ("new", "in_process"))
            rec.exception_count = len(active)
            rec.blocking_exception_count = len(active.filtered("is_blocking"))

    def action_approve_expense_sheets(self):
        """Gate: block approval if unresolved blocking exceptions exist."""
        for sheet in self:
            if sheet.blocking_exception_count > 0:
                raise UserError(
                    f"{sheet.blocking_exception_count} blocking exception(s) "
                    "must be resolved before approval."
                )
        return super().action_approve_expense_sheets()
