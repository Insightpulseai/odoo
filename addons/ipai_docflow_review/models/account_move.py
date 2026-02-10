from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    _sql_constraints = [
        (
            "uniq_vendor_invoice_soft",
            "UNIQUE(partner_id, ref, amount_total, invoice_date)",
            "Possible duplicate vendor bill detected (Partner + Ref + Amount + Date are identical).",
        )
    ]
