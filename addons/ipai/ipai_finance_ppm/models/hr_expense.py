import base64
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):
    """Extend hr.expense with Pulser AI Action Proposals."""

    _inherit = "hr.expense"

    pulser_proposal_id = fields.Char(
        string="Pulser Proposal ID",
        help="ID of the AI action proposal that generated this record.",
        copy=False,
    )
    is_pulser_draft = fields.Boolean(
        string="Is Pulser Draft",
        default=False,
        help="True if this expense was drafted by the Pulser Assistant.",
    )

    @api.model
    def action_pulser_draft_expense(self, proposal_data):
        """Tool binding for Pulser to create an hr.expense draft with attachment.

        Expected proposal_data: {
            "name": str,
            "total_amount_currency": float,
            "currency_id": int/str,
            "date": str,
            "employee_id": int/str,
            "product_id": int/str,
            "proposal_id": str,
            "attachment_base64": str (optional),
            "attachment_name": str (optional)
        }
        """
        _logger.info("Pulser: Handling expense draft proposal %s", proposal_data.get("proposal_id"))

        # Resolve IDs
        employee = self.env["hr.employee"].sudo().search([
            "|", ("name", "ilike", str(proposal_data.get("employee_id"))),
            ("user_id.login", "=", str(proposal_data.get("employee_id")))
        ], limit=1)

        product = self.env["product.product"].sudo().search([
            "|", ("name", "ilike", str(proposal_data.get("product_id"))),
            ("default_code", "=", str(proposal_data.get("product_id")))
        ], limit=1)

        if not employee:
            raise UserError(_("Pulser: Could not resolve employee for expense draft."))

        vals = {
            "name": proposal_data.get("name", "Pulser Draft Expense"),
            "total_amount_currency": proposal_data.get("total_amount_currency", 0.0),
            "date": proposal_data.get("date", fields.Date.today()),
            "employee_id": employee.id,
            "product_id": product.id if product else self.env.ref("hr_expense.product_product_fixed_cost", raise_if_not_found=False).id or self.env.ref("hr_expense.expense_product_communication").id,
            "pulser_proposal_id": proposal_data.get("proposal_id"),
            "is_pulser_draft": True,
        }

        expense = self.sudo().create(vals)

        # Handle attachment if provided (Requirement: "Attach a file")
        if proposal_data.get("attachment_base64"):
            self.env["ir.attachment"].sudo().create({
                "name": proposal_data.get("attachment_name") or "pulser_receipt.pdf",
                "type": "binary",
                "datas": proposal_data.get("attachment_base64"),
                "res_model": "hr.expense",
                "res_id": expense.id,
                "mimetype": "application/pdf" if ".pdf" in (proposal_data.get("attachment_name") or "") else "image/jpeg",
            })
            _logger.info("Pulser: Linked attachment to expense %s", expense.id)

        return {
            "id": expense.id,
            "status": "drafted",
            "message": f"Expense draft {expense.name} created for {employee.name} with attachment.",
        }
