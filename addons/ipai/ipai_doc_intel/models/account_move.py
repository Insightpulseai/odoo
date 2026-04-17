# -*- coding: utf-8 -*-
"""Extend account.move with Document Intelligence extraction."""
import base64
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    x_docai_status = fields.Selection(
        [
            ("none", "Not Extracted"),
            ("extracting", "Extracting..."),
            ("extracted", "Extracted"),
            ("review", "Needs Review"),
            ("failed", "Failed"),
        ],
        string="DocAI Status",
        default="none",
        tracking=True,
    )
    x_docai_confidence = fields.Float(
        string="DocAI Confidence",
        digits=(5, 3),
        readonly=True,
    )
    x_docai_raw_result = fields.Text(
        string="DocAI Raw Result",
        readonly=True,
    )

    def action_extract_with_docai(self):
        """Extract invoice data from attached PDF using Azure Document Intelligence."""
        self.ensure_one()

        if self.move_type not in ("in_invoice", "in_refund"):
            raise UserError("Document extraction is only available for vendor bills.")

        # Find the first PDF/image attachment
        attachment = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "account.move"),
                ("res_id", "=", self.id),
                ("mimetype", "in", [
                    "application/pdf",
                    "image/jpeg",
                    "image/png",
                    "image/tiff",
                ]),
            ],
            limit=1,
            order="create_date desc",
        )
        if not attachment:
            raise UserError(
                "No PDF or image attachment found. "
                "Please attach the invoice document first."
            )

        self.x_docai_status = "extracting"
        self.env.cr.commit()  # Show status to user immediately

        try:
            # Get file content
            file_content = base64.b64decode(attachment.datas)
            content_type = attachment.mimetype

            # Call DocAI service
            service = self.env["ipai.doc.intel.service"]
            result = service.analyze_invoice(file_content, content_type)

            # Store raw result
            import json
            self.x_docai_raw_result = json.dumps(result, indent=2, default=str)
            self.x_docai_confidence = result.get("avg_confidence", 0)

            # Apply extracted fields
            fields_data = result.get("fields", {})
            self._apply_docai_fields(fields_data)

            # Set status based on confidence
            if result.get("needs_review"):
                self.x_docai_status = "review"
                self.message_post(
                    body=(
                        f"<b>DocAI extraction complete — NEEDS REVIEW</b><br/>"
                        f"Confidence: {result['avg_confidence']:.1%}<br/>"
                        f"Some fields may be inaccurate. Please verify before posting."
                    ),
                    message_type="notification",
                )
            else:
                self.x_docai_status = "extracted"
                self.message_post(
                    body=(
                        f"<b>DocAI extraction complete</b><br/>"
                        f"Confidence: {result['avg_confidence']:.1%}<br/>"
                        f"Fields populated from document. Review and post."
                    ),
                    message_type="notification",
                )

            _logger.info(
                "DocAI extraction for move %s: confidence=%s, auto_create=%s",
                self.id, result["avg_confidence"], result.get("auto_create"),
            )

        except Exception as e:
            self.x_docai_status = "failed"
            self.message_post(
                body=f"<b>DocAI extraction failed:</b> {str(e)[:200]}",
                message_type="notification",
            )
            _logger.exception("DocAI extraction failed for move %s", self.id)
            raise

    def _apply_docai_fields(self, fields_data):
        """Apply extracted DocAI fields to the account.move record."""
        vals = {}

        # Invoice reference
        ref = fields_data.get("invoice_ref", {}).get("value")
        if ref:
            vals["ref"] = ref

        # Invoice date
        inv_date = fields_data.get("invoice_date", {}).get("value")
        if inv_date:
            vals["invoice_date"] = inv_date

        # Due date
        due_date = fields_data.get("due_date", {}).get("value")
        if due_date:
            vals["invoice_date_due"] = due_date

        # Vendor (partner) — lookup or log for manual assignment
        vendor_name = fields_data.get("vendor_name", {}).get("value")
        if vendor_name:
            partner = self.env["res.partner"].search(
                [("name", "ilike", vendor_name), ("supplier_rank", ">", 0)],
                limit=1,
            )
            if partner:
                vals["partner_id"] = partner.id
            else:
                # Log vendor name for manual assignment
                self.message_post(
                    body=(
                        f"<b>Vendor not found:</b> {vendor_name}<br/>"
                        f"Please assign the vendor manually or create a new contact."
                    ),
                    message_type="notification",
                )

        # Vendor TIN
        vendor_tin = fields_data.get("vendor_tax_id", {}).get("value")
        if vendor_tin and vals.get("partner_id"):
            partner = self.env["res.partner"].browse(vals["partner_id"])
            if not partner.vat:
                partner.vat = vendor_tin

        # Apply header fields
        if vals:
            self.write(vals)

        # Apply line items if available
        line_items = fields_data.get("line_items")
        if line_items and isinstance(line_items, list):
            self._apply_docai_lines(line_items)

    def _apply_docai_lines(self, line_items):
        """Create invoice lines from DocAI extracted line items."""
        # Only apply to draft invoices with no existing lines (or 1 auto-created line)
        existing_lines = self.invoice_line_ids.filtered(
            lambda l: l.display_type not in ("line_section", "line_note")
        )
        if len(existing_lines) > 1:
            _logger.info(
                "Skipping line creation — move %s already has %s lines",
                self.id, len(existing_lines),
            )
            return

        for item in line_items:
            description = item.get("description")
            amount = item.get("amount") or item.get("unit_price")
            quantity = item.get("quantity") or 1

            if description and amount:
                self.write({
                    "invoice_line_ids": [(0, 0, {
                        "name": description,
                        "quantity": quantity,
                        "price_unit": amount / quantity if quantity else amount,
                    })],
                })
