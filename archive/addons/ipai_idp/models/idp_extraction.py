# -*- coding: utf-8 -*-
"""
IDP Extraction Model.

Stores LLM-based extraction results with versioned model tracking.
"""
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IdpExtraction(models.Model):
    """
    IDP Extraction Results.

    Stores the structured data extracted by the LLM from OCR text.
    Tracks which model version was used for reproducibility.

    Attributes:
        _name: idp.extraction
        _description: IDP Extraction Results
    """

    _name = "idp.extraction"
    _description = "IDP Extraction Results"
    _order = "create_date desc"

    # Core fields
    document_id = fields.Many2one(
        "idp.document",
        string="Document",
        required=True,
        ondelete="cascade",
    )
    ocr_id = fields.Many2one(
        "idp.document.ocr",
        string="OCR Source",
        help="The OCR result used for extraction",
    )
    model_version_id = fields.Many2one(
        "idp.model.version",
        string="Model Version",
        help="The prompt/model version used for extraction",
    )

    # Extraction results
    doc_type = fields.Selection(
        related="document_id.doc_type",
        string="Document Type",
        store=True,
    )
    extracted_json = fields.Text(
        string="Extracted Data (JSON)",
        help="Structured extraction result in JSON format",
    )
    raw_llm_response = fields.Text(
        string="Raw LLM Response",
        help="Complete LLM response for debugging",
    )

    # Confidence and quality
    confidence = fields.Float(
        string="Confidence Score",
        help="Overall extraction confidence (0.0-1.0)",
    )
    field_confidences = fields.Text(
        string="Field Confidences (JSON)",
        help="Per-field confidence scores",
    )

    # Validation results
    validation_status = fields.Selection(
        [
            ("pending", "Pending"),
            ("pass", "Pass"),
            ("fail", "Fail"),
            ("warning", "Warning"),
        ],
        string="Validation Status",
        default="pending",
    )
    validation_errors = fields.Text(
        string="Validation Errors (JSON)",
        help="List of validation errors/warnings",
    )

    # Processing metadata
    processing_time_ms = fields.Integer(
        string="Processing Time (ms)",
    )
    llm_model = fields.Char(
        string="LLM Model",
        help="The actual LLM model used (e.g., claude-3-sonnet)",
    )
    token_count = fields.Integer(
        string="Token Count",
        help="Total tokens used in the LLM call",
    )

    # ADE (Agentic Document Extraction) fields
    ade_pipeline_id = fields.Char(
        string="ADE Pipeline ID",
        help="Identifier of the ADE pipeline used (e.g., invoice_basic_v1)",
        index=True,
    )
    ade_status = fields.Selection(
        [
            ("ok", "OK"),
            ("needs_review", "Needs Review"),
            ("failed", "Failed"),
        ],
        string="ADE Status",
        default="ok",
        help="Final status returned by the ADE orchestrator",
    )
    ade_trace = fields.Text(
        string="ADE Trace (JSON)",
        help="Full step-by-step trace from ADE orchestrator",
    )
    ade_action = fields.Char(
        string="ADE Action",
        help="Action taken by ADE (e.g., send_to_review)",
    )
    ade_reason = fields.Text(
        string="ADE Reason",
        help="Reason for ADE status if not OK",
    )

    # Computed fields for easy access
    vendor_name = fields.Char(
        string="Vendor Name",
        compute="_compute_extracted_fields",
        store=True,
    )
    invoice_number = fields.Char(
        string="Invoice Number",
        compute="_compute_extracted_fields",
        store=True,
    )
    invoice_date = fields.Date(
        string="Invoice Date",
        compute="_compute_extracted_fields",
        store=True,
    )
    total_amount = fields.Float(
        string="Total Amount",
        compute="_compute_extracted_fields",
        store=True,
    )
    currency = fields.Char(
        string="Currency",
        compute="_compute_extracted_fields",
        store=True,
    )

    @api.depends("extracted_json")
    def _compute_extracted_fields(self):
        """Parse JSON and populate computed fields."""
        for record in self:
            data = {}
            if record.extracted_json:
                try:
                    data = json.loads(record.extracted_json)
                except json.JSONDecodeError:
                    _logger.warning(
                        "Failed to parse extracted_json for extraction %s",
                        record.id,
                    )

            record.vendor_name = data.get("vendor_name") or data.get("merchant_name")
            record.invoice_number = data.get("invoice_number")
            record.total_amount = data.get("total") or data.get("total_amount") or 0.0
            record.currency = data.get("currency")

            # Parse date
            date_str = data.get("invoice_date") or data.get("transaction_date")
            if date_str:
                try:
                    record.invoice_date = fields.Date.from_string(date_str)
                except (ValueError, TypeError):
                    record.invoice_date = False
            else:
                record.invoice_date = False

    def get_extracted_data(self):
        """
        Return extracted data as a Python dict.

        Returns:
            dict: Parsed extraction data
        """
        self.ensure_one()
        if self.extracted_json:
            try:
                return json.loads(self.extracted_json)
            except json.JSONDecodeError:
                return {}
        return {}

    def get_line_items(self):
        """
        Extract line items from the extraction.

        Returns:
            list: List of line item dicts
        """
        data = self.get_extracted_data()
        return data.get("line_items") or data.get("items") or []

    def action_validate(self):
        """Run validation on this extraction."""
        validator = self.env["idp.service.validator"]
        for record in self:
            result = validator.validate(record)
            record.write(
                {
                    "validation_status": result.get("status", "fail"),
                    "validation_errors": json.dumps(result.get("errors", [])),
                }
            )
