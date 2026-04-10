# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

"""Copilot invoice check model.

Persists the result of the ph_invoice_math validator so findings
can be linked to a conversation/attachment and reviewed by the user.
"""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CopilotInvoiceCheck(models.Model):
    _name = "ipai.copilot.invoice.check"
    _description = "Copilot Invoice Check"
    _order = "create_date desc, id desc"

    # -------------------------------------------------------------------------
    # Relation to attachment
    # -------------------------------------------------------------------------
    attachment_ref_id = fields.Many2one(
        "ipai.copilot.attachment.ref",
        string="Attachment Reference",
        ondelete="cascade",
        index=True,
    )

    # -------------------------------------------------------------------------
    # Validation outcome
    # -------------------------------------------------------------------------
    status = fields.Selection(
        [
            ("validated", "Validated"),
            ("needs_review", "Needs Review"),
            ("error", "Error"),
        ],
        required=True,
        default="needs_review",
        index=True,
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
        help="expected_payable minus printed_total_due",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.PHP", raise_if_not_found=False),
    )
    findings_json = fields.Text(
        string="Findings (JSON)",
        default="[]",
    )
    summary = fields.Text(
        string="Summary",
    )
