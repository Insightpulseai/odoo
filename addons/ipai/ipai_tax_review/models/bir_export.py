"""TaxPulse PH — BIR export and compliance dataset model.

Phase 4: Structured compliance exports and BIR-oriented reporting.
Constitution: produce compliance-ready structured outputs.
"""

import json

from odoo import api, fields, models


class BIRExportBatch(models.Model):
    _name = "ipai.bir.export.batch"
    _description = "BIR Export Batch"
    _order = "create_date desc"

    name = fields.Char(
        string="Batch Reference",
        required=True,
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("ipai.bir.export.batch") or "/",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("generated", "Generated"),
            ("exported", "Exported"),
        ],
        string="Status",
        default="draft",
        required=True,
    )
    export_type = fields.Selection(
        [
            ("purchases", "Purchase Journal (SLSP)"),
            ("sales", "Sales Journal (SLSP)"),
            ("withholding", "Withholding Summary (2307)"),
            ("vat_relief", "VAT Relief Summary"),
        ],
        string="Export Type",
        required=True,
        default="purchases",
    )
    review_ids = fields.Many2many(
        "ipai.tax.review",
        string="Included Reviews",
    )
    review_count = fields.Integer(
        string="Review Count",
        compute="_compute_review_count",
    )
    export_data = fields.Text(
        string="Export Data (JSON)",
        help="Structured JSON export for compliance reporting",
    )
    notes = fields.Text(string="Notes")

    @api.depends("review_ids")
    def _compute_review_count(self):
        for batch in self:
            batch.review_count = len(batch.review_ids)

    def action_generate(self):
        """Generate structured compliance dataset from included reviews."""
        self.ensure_one()
        records = []
        for review in self.review_ids:
            move = review.move_id
            records.append({
                "review_ref": review.name,
                "move_name": move.name if move else "",
                "partner_name": move.partner_id.name if move and move.partner_id else "",
                "partner_vat": move.partner_id.vat if move and move.partner_id else "",
                "date": str(move.date) if move else "",
                "expected_subtotal": float(review.expected_subtotal),
                "expected_vat": float(review.expected_vat),
                "expected_withholding": float(review.expected_withholding),
                "expected_payable": float(review.expected_payable),
                "printed_total_due": float(review.printed_total_due),
                "delta": float(review.delta),
                "state": review.state,
                "extraction_confidence": float(review.extraction_confidence),
            })

        export = {
            "batch_ref": self.name,
            "company": self.company_id.name,
            "company_vat": self.company_id.vat or "",
            "date_from": str(self.date_from),
            "date_to": str(self.date_to),
            "export_type": self.export_type,
            "record_count": len(records),
            "records": records,
        }
        self.write({
            "export_data": json.dumps(export, indent=2, ensure_ascii=False),
            "state": "generated",
        })

    def action_mark_exported(self):
        """Mark batch as exported (downloaded/transmitted)."""
        self.ensure_one()
        self.state = "exported"

    def action_reset_to_draft(self):
        """Reset to draft for regeneration."""
        self.ensure_one()
        self.write({
            "state": "draft",
            "export_data": False,
        })
