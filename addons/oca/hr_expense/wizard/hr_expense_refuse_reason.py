# Copyright 2024 IPAI - InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class HrExpenseRefuseWizard(models.TransientModel):
    """Wizard to refuse expense reports with a reason."""

    _name = "hr.expense.refuse.wizard"
    _description = "Expense Refuse Reason Wizard"

    sheet_id = fields.Many2one(
        "hr.expense.sheet",
        string="Expense Report",
        required=True,
    )
    reason = fields.Text(
        string="Reason",
        required=True,
    )

    def action_refuse(self):
        """Refuse the expense report with the given reason."""
        self.ensure_one()
        self.sheet_id.write({"state": "cancel"})
        self.sheet_id.expense_line_ids.write({"state": "refused"})
        self.sheet_id.message_post(
            body=_("Expense report refused. Reason: %s") % self.reason,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        return {"type": "ir.actions.act_window_close"}
