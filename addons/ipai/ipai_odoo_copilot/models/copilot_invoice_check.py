# -*- coding: utf-8 -*-
from odoo import fields, models


class CopilotInvoiceCheck(models.Model):
    """Stores deterministic PH invoice math validation results.

    The validator (``validators.ph_invoice_math``) runs outside Odoo and
    produces a result dict.  This model persists those results so the
    copilot conversation can reference them and Odoo workflows can gate
    on the ``status`` field.
    """

    _name = "ipai.copilot.invoice.check"
    _description = "Copilot Invoice Math Check"
    _order = "create_date desc"

    attachment_ref_id = fields.Many2one(
        comodel_name="ipai.copilot.attachment.ref",
        string="Attachment Reference",
        ondelete="cascade",
        index=True,
    )
    status = fields.Selection(
        selection=[
            ("validated", "Validated"),
            ("needs_review", "Needs Review"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        required=True,
        default="needs_review",
    )
    expected_payable = fields.Float(
        string="Expected Payable",
        digits=(16, 2),
    )
    printed_total_due = fields.Float(
        string="Printed Total Due",
        digits=(16, 2),
    )
    delta = fields.Float(
        string="Delta",
        digits=(16, 2),
        help="expected_payable - printed_total_due",
    )
    findings_json = fields.Text(
        string="Findings (JSON)",
        help="JSON array of finding objects from the deterministic validator.",
    )
    summary = fields.Text(
        string="Summary",
        help="Human-readable explanation of validation results.",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.PHP", raise_if_not_found=False),
    )
