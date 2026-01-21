import hashlib
import json
import logging
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):
    """Extend hr.expense with OCR capabilities."""

    _inherit = "hr.expense"

    # OCR fields
    ocr_result_id = fields.Many2one(
        "ipai.expense.ocr.result",
        string="OCR Result",
        ondelete="set null",
    )
    ocr_state = fields.Selection(
        related="ocr_result_id.state",
        string="OCR Status",
        store=True,
    )
    receipt_hash = fields.Char(
        string="Receipt Hash",
        help="SHA256 hash of the receipt file for duplicate detection",
        index=True,
    )
    ocr_extracted_text = fields.Text(
        related="ocr_result_id.extracted_text",
        string="OCR Text",
    )
    ocr_confidence = fields.Float(
        related="ocr_result_id.confidence",
        string="OCR Confidence",
    )

    # Duplicate detection
    is_duplicate_receipt = fields.Boolean(
        string="Potential Duplicate",
        compute="_compute_is_duplicate",
        store=True,
    )
    duplicate_expense_ids = fields.Many2many(
        "hr.expense",
        "hr_expense_duplicate_rel",
        "expense_id",
        "duplicate_id",
        string="Duplicate Expenses",
        compute="_compute_is_duplicate",
        store=True,
    )

    @api.depends("receipt_hash")
    def _compute_is_duplicate(self):
        """Check for duplicate receipts based on hash."""
        ICP = self.env["ir.config_parameter"].sudo()
        duplicate_days = int(ICP.get_param("ipai_expense_ocr.duplicate_days", "90"))
        cutoff_date = datetime.now() - timedelta(days=duplicate_days)

        for expense in self:
            if not expense.receipt_hash:
                expense.is_duplicate_receipt = False
                expense.duplicate_expense_ids = False
                continue

            # Find other expenses with same hash
            duplicates = self.search(
                [
                    ("id", "!=", expense.id),
                    ("receipt_hash", "=", expense.receipt_hash),
                    ("create_date", ">=", cutoff_date),
                ]
            )

            expense.is_duplicate_receipt = bool(duplicates)
            expense.duplicate_expense_ids = duplicates

    def _compute_receipt_hash(self, attachment):
        """Compute SHA256 hash of attachment content."""
        if not attachment or not attachment.datas:
            return False

        import base64

        content = base64.b64decode(attachment.datas)
        return hashlib.sha256(content).hexdigest()

    def action_scan_receipt(self):
        """Trigger OCR scan on the expense receipt."""
        self.ensure_one()

        # Find receipt attachment
        attachments = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "hr.expense"),
                ("res_id", "=", self.id),
            ],
            limit=1,
            order="create_date desc",
        )

        if not attachments:
            raise UserError(
                _("No receipt attachment found. Please upload a receipt first.")
            )

        attachment = attachments[0]

        # Compute hash for duplicate detection
        self.receipt_hash = self._compute_receipt_hash(attachment)

        # Check for duplicates
        if self.is_duplicate_receipt:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Potential Duplicate"),
                    "message": _(
                        "This receipt may have already been submitted. Please review."
                    ),
                    "type": "warning",
                    "sticky": True,
                },
            }

        # Create OCR result record
        ocr_result = self.env["ipai.expense.ocr.result"].create(
            {
                "expense_id": self.id,
                "attachment_id": attachment.id,
                "state": "queued",
            }
        )
        self.ocr_result_id = ocr_result

        # Trigger extraction
        ocr_result.action_extract()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("OCR Started"),
                "message": _(
                    "Receipt is being processed. Fields will be updated automatically."
                ),
                "type": "info",
            },
        }

    def action_apply_ocr_fields(self):
        """Apply extracted OCR fields to the expense."""
        self.ensure_one()

        if not self.ocr_result_id or self.ocr_result_id.state != "extracted":
            raise UserError(_("No OCR results available to apply."))

        result = self.ocr_result_id

        values = {}

        # Apply merchant name
        if result.merchant_name and not self.name:
            values["name"] = result.merchant_name

        # Apply amount
        if result.total_amount and not self.total_amount_company:
            values["total_amount_company"] = result.total_amount

        # Apply date
        if result.receipt_date and not self.date:
            values["date"] = result.receipt_date

        if values:
            self.write(values)
            result.state = "applied"
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Fields Applied"),
                    "message": _(
                        "OCR extracted fields have been applied to the expense."
                    ),
                    "type": "success",
                },
            }
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("No Changes"),
                    "message": _(
                        "No new fields to apply (expense already has values)."
                    ),
                    "type": "warning",
                },
            }
