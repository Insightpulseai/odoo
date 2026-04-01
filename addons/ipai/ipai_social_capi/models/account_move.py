"""Account Move extension — relay invoice_paid events to Meta CAPI bridge."""

import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    capi_event_ids = fields.One2many(
        "ipai.capi.event.log",
        "res_id",
        string="CAPI Events",
        domain=[("res_model", "=", "account.move")],
    )

    def _get_reconciled_payments(self):
        """Override point — called after payment reconciliation in CE."""
        result = super()._get_reconciled_payments()
        # Check if this invoice just became fully paid
        for move in self:
            if (
                move.move_type == "out_invoice"
                and move.payment_state == "paid"
            ):
                move._fire_capi_invoice_paid()
        return result

    def action_register_payment(self):
        """Hook payment registration to detect paid invoices."""
        result = super().action_register_payment()
        return result

    def write(self, vals):
        """Detect payment_state transition to 'paid' for customer invoices."""
        old_states = {
            move.id: move.payment_state
            for move in self
            if move.move_type == "out_invoice"
        }
        result = super().write(vals)

        if "payment_state" in vals and vals["payment_state"] == "paid":
            for move in self:
                if (
                    move.move_type == "out_invoice"
                    and old_states.get(move.id) != "paid"
                ):
                    move._fire_capi_invoice_paid()

        return result

    def _fire_capi_invoice_paid(self):
        """Send invoice_paid event to CAPI bridge."""
        self.ensure_one()

        partner = self.partner_id
        if not partner:
            return

        user_data = {}
        if partner.email:
            user_data["email"] = partner.email
        if partner.phone:
            user_data["phone"] = partner.phone

        if partner.name:
            parts = partner.name.split(" ", 1)
            user_data["first_name"] = parts[0]
            if len(parts) > 1:
                user_data["last_name"] = parts[1]

        if partner.country_id:
            user_data["country_code"] = partner.country_id.code
        if partner.city:
            user_data["city"] = partner.city

        # Must have email or phone
        if not user_data.get("email") and not user_data.get("phone"):
            return

        custom_data = {
            "value": self.amount_total,
            "currency": self.currency_id.name or "PHP",
            "order_id": self.name or "",
        }

        self.env["ipai.capi.event.log"].send_event(
            event_type="invoice_paid",
            record=self,
            user_data=user_data,
            custom_data=custom_data,
        )
