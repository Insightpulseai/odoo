# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IPAIApprovalDelegate(models.TransientModel):
    """Wizard to delegate an approval to another user."""

    _name = "ipai.approval.delegate.wizard"
    _description = "Delegate Approval Wizard"

    approver_id = fields.Many2one(
        "ipai.approval.approver", required=True, string="Approval Record"
    )
    delegate_to_id = fields.Many2one(
        "res.users", required=True, string="Delegate To", domain=[("active", "=", True)]
    )
    reason = fields.Text(string="Reason for Delegation")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get("active_model") == "ipai.approval.approver":
            res["approver_id"] = self.env.context.get("active_id")
        return res

    def action_delegate(self):
        """Execute the delegation."""
        self.ensure_one()
        if not self.approver_id or not self.delegate_to_id:
            raise UserError(_("Please select a user to delegate to."))

        if self.delegate_to_id == self.approver_id.user_id:
            raise UserError(_("Cannot delegate to yourself."))

        self.approver_id.action_delegate(self.delegate_to_id)

        return {"type": "ir.actions.act_window_close"}
