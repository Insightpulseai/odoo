import json
import logging
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiDocument(models.Model):
    """Document with OCR extraction results."""

    _name = "ipai.document"
    _description = "IPAI Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Attachment",
        required=True,
        ondelete="cascade",
    )
    res_model = fields.Char(
        string="Related Model",
        index=True,
    )
    res_id = fields.Integer(
        string="Related Record ID",
        index=True,
    )
    doc_type = fields.Selection(
        [
            ("invoice", "Invoice"),
            ("bill", "Bill"),
            ("receipt", "Receipt"),
            ("contract", "Contract"),
            ("purchase_order", "Purchase Order"),
            ("other", "Other"),
        ],
        string="Document Type",
        default="other",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("processing", "Processing"),
            ("ready", "Ready for Review"),
            ("applied", "Applied"),
            ("failed", "Failed"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )
    extracted_text = fields.Text(
        string="Extracted Text",
    )
    extraction_json = fields.Text(
        string="Extraction Data (JSON)",
    )
    confidence = fields.Float(
        string="Confidence",
        digits=(4, 2),
    )
    ocr_job_id = fields.Char(
        string="OCR Job ID",
    )
    error_message = fields.Text(
        string="Error Message",
    )
    processing_duration = fields.Float(
        string="Processing Duration (seconds)",
    )
    requires_manual_review = fields.Boolean(
        string="Requires Manual Review",
        default=False,
    )

    # Extracted fields (common)
    vendor_name = fields.Char(
        string="Vendor Name",
        compute="_compute_extracted_fields",
        store=True,
    )
    document_date = fields.Date(
        string="Document Date",
        compute="_compute_extracted_fields",
        store=True,
    )
    document_number = fields.Char(
        string="Document Number",
        compute="_compute_extracted_fields",
        store=True,
    )
    currency_code = fields.Char(
        string="Currency",
        compute="_compute_extracted_fields",
        store=True,
    )
    subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_extracted_fields",
        store=True,
    )
    tax_amount = fields.Float(
        string="Tax Amount",
        compute="_compute_extracted_fields",
        store=True,
    )
    total_amount = fields.Float(
        string="Total Amount",
        compute="_compute_extracted_fields",
        store=True,
    )

    @api.depends("extraction_json")
    def _compute_extracted_fields(self):
        """Extract common fields from OCR JSON result."""
        for record in self:
            if not record.extraction_json:
                record.vendor_name = False
                record.document_date = False
                record.document_number = False
                record.currency_code = False
                record.subtotal = 0.0
                record.tax_amount = 0.0
                record.total_amount = 0.0
                continue

            try:
                data = json.loads(record.extraction_json)
                fields_data = data.get("fields", {})

                record.vendor_name = self._get_field_value(fields_data, "vendor_name")
                record.document_number = self._get_field_value(
                    fields_data, "invoice_number"
                ) or self._get_field_value(fields_data, "document_number")
                record.currency_code = self._get_field_value(fields_data, "currency")
                record.subtotal = self._get_field_value(fields_data, "subtotal") or 0.0
                record.tax_amount = self._get_field_value(fields_data, "tax") or 0.0
                record.total_amount = self._get_field_value(fields_data, "total") or 0.0

                # Parse date
                date_str = self._get_field_value(
                    fields_data, "invoice_date"
                ) or self._get_field_value(fields_data, "document_date")
                if date_str:
                    try:
                        record.document_date = fields.Date.from_string(date_str)
                    except (ValueError, TypeError):
                        record.document_date = False
                else:
                    record.document_date = False

            except (json.JSONDecodeError, KeyError) as e:
                _logger.warning(f"Failed to parse extraction JSON: {e}")
                record.vendor_name = False
                record.document_date = False
                record.document_number = False
                record.currency_code = False
                record.subtotal = 0.0
                record.tax_amount = 0.0
                record.total_amount = 0.0

    @staticmethod
    def _get_field_value(fields_data, field_name):
        """Get value from OCR fields dict (handles nested structure)."""
        field = fields_data.get(field_name, {})
        if isinstance(field, dict):
            return field.get("value")
        return field

    def get_confidence_for_field(self, field_name):
        """Get confidence score for a specific field."""
        self.ensure_one()
        if not self.extraction_json:
            return 0.0
        try:
            data = json.loads(self.extraction_json)
            fields_data = data.get("fields", {})
            field = fields_data.get(field_name, {})
            if isinstance(field, dict):
                return field.get("conf", 0.0)
            return 0.0
        except (json.JSONDecodeError, KeyError):
            return 0.0

    def action_extract(self):
        """Send document to OCR service for extraction."""
        self.ensure_one()

        if not self.attachment_id:
            raise UserError(_("No attachment found."))

        self.state = "processing"
        self.error_message = False

        ocr_service = self.env["ipai.ocr.service"]

        try:
            start_time = datetime.now()

            result = ocr_service.extract_document(
                self.attachment_id.datas,
                self.attachment_id.name,
            )

            duration = (datetime.now() - start_time).total_seconds()

            self.write(
                {
                    "state": "ready",
                    "extracted_text": result.get("text", ""),
                    "extraction_json": json.dumps(result),
                    "doc_type": result.get("doc_type", "other"),
                    "confidence": self._compute_overall_confidence(result),
                    "processing_duration": duration,
                    "requires_manual_review": self._needs_manual_review(result),
                }
            )

            _logger.info(
                f"OCR extraction completed for document {self.id}, "
                f"confidence={self.confidence:.2f}"
            )

        except Exception as e:
            _logger.error(f"OCR extraction failed for document {self.id}: {e}")
            self.write(
                {
                    "state": "failed",
                    "error_message": str(e),
                }
            )
            raise UserError(_("OCR extraction failed: %s") % str(e))

    def _compute_overall_confidence(self, result):
        """Compute overall confidence from extracted fields."""
        fields_data = result.get("fields", {})
        if not fields_data:
            return 0.0

        confidences = []
        for field in fields_data.values():
            if isinstance(field, dict) and "conf" in field:
                confidences.append(field["conf"])

        if not confidences:
            return 0.0

        return sum(confidences) / len(confidences)

    def _needs_manual_review(self, result):
        """Check if document needs manual review based on confidence."""
        confidence = self._compute_overall_confidence(result)
        threshold = float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_document_ai.review_threshold", "0.70")
        )
        return confidence < threshold

    def action_apply_to_record(self):
        """Apply extracted fields to the related record."""
        self.ensure_one()

        if self.state != "ready":
            raise UserError(_("Document must be in 'Ready for Review' state."))

        if not self.res_model or not self.res_id:
            raise UserError(_("No related record configured."))

        # Get the target record
        target = self.env[self.res_model].browse(self.res_id)
        if not target.exists():
            raise UserError(_("Related record not found."))

        # Apply fields based on model type
        mapping = self._get_field_mapping(self.res_model)
        values = {}

        for source_field, target_field in mapping.items():
            value = getattr(self, source_field, None)
            if value and hasattr(target, target_field):
                values[target_field] = value

        if values:
            target.write(values)
            _logger.info(
                f"Applied OCR fields to {self.res_model}/{self.res_id}: {values.keys()}"
            )

        self.state = "applied"
        return True

    def _get_field_mapping(self, model):
        """Get field mapping for a model."""
        mappings = {
            "account.move": {
                "vendor_name": "partner_id",  # Needs partner lookup
                "document_date": "invoice_date",
                "document_number": "ref",
            },
            "hr.expense": {
                "vendor_name": "name",
                "document_date": "date",
                "total_amount": "total_amount",
            },
            "purchase.order": {
                "vendor_name": "partner_id",
                "document_date": "date_order",
            },
        }
        return mappings.get(model, {})

    def action_retry(self):
        """Retry failed extraction."""
        self.ensure_one()
        if self.state != "failed":
            raise UserError(_("Only failed documents can be retried."))

        self.state = "draft"
        self.error_message = False
        return self.action_extract()

    def action_reset(self):
        """Reset document to draft state."""
        self.ensure_one()
        self.write(
            {
                "state": "draft",
                "extracted_text": False,
                "extraction_json": False,
                "confidence": 0.0,
                "error_message": False,
            }
        )
