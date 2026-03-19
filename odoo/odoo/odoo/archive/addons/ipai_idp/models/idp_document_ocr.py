# -*- coding: utf-8 -*-
"""
IDP Document OCR Model.

Stores OCR processing results for documents.
"""
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IdpDocumentOcr(models.Model):
    """
    IDP Document OCR Results.

    Stores the raw OCR text output and bounding box data for a document.
    Multiple OCR results can exist for a document (different engines, retries).

    Attributes:
        _name: idp.document.ocr
        _description: IDP Document OCR Results
    """

    _name = "idp.document.ocr"
    _description = "IDP Document OCR Results"
    _order = "create_date desc"

    # Core fields
    document_id = fields.Many2one(
        "idp.document",
        string="Document",
        required=True,
        ondelete="cascade",
    )
    raw_text = fields.Text(
        string="Raw OCR Text",
        help="Full extracted text from OCR",
    )
    ocr_engine = fields.Selection(
        [
            ("tesseract", "Tesseract"),
            ("paddleocr", "PaddleOCR"),
            ("google_vision", "Google Vision"),
            ("azure", "Azure Form Recognizer"),
            ("insightpulse", "InsightPulse OCR"),
            ("other", "Other"),
        ],
        string="OCR Engine",
        default="insightpulse",
        required=True,
    )
    engine_version = fields.Char(
        string="Engine Version",
        help="Version of the OCR engine used",
    )

    # Quality metrics
    confidence = fields.Float(
        string="Overall Confidence",
        help="Average OCR confidence score (0.0-1.0)",
    )
    word_count = fields.Integer(
        string="Word Count",
        compute="_compute_word_count",
        store=True,
    )
    character_count = fields.Integer(
        string="Character Count",
        compute="_compute_character_count",
        store=True,
    )

    # Bounding box data (JSON)
    bounding_boxes = fields.Text(
        string="Bounding Boxes (JSON)",
        help="Word/line bounding boxes in JSON format",
    )

    # Processing metadata
    processing_time_ms = fields.Integer(
        string="Processing Time (ms)",
        help="Time taken for OCR processing",
    )
    pages_processed = fields.Integer(
        string="Pages Processed",
        default=1,
    )

    # Status
    status = fields.Selection(
        [
            ("success", "Success"),
            ("partial", "Partial"),
            ("failed", "Failed"),
        ],
        string="Status",
        default="success",
        required=True,
    )
    error_message = fields.Text(
        string="Error Message",
    )

    @api.depends("raw_text")
    def _compute_word_count(self):
        """Count words in OCR text."""
        for record in self:
            if record.raw_text:
                record.word_count = len(record.raw_text.split())
            else:
                record.word_count = 0

    @api.depends("raw_text")
    def _compute_character_count(self):
        """Count characters in OCR text."""
        for record in self:
            record.character_count = len(record.raw_text or "")
