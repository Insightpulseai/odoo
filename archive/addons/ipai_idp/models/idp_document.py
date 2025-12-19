# -*- coding: utf-8 -*-
"""
IDP Document Model.

Core model for storing documents to be processed by the IDP engine.
Tracks document lifecycle from upload through extraction to export.
"""
import hashlib
import logging

from odoo.exceptions import UserError

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class IdpDocument(models.Model):
    """
    IDP Document Model.

    Represents a document (invoice, receipt, PO, etc.) to be processed
    through the IDP pipeline. Tracks status, source, and processing history.

    Lifecycle:
        queued -> processing -> classified -> extracted -> validated ->
        approved/review_needed -> exported

    Attributes:
        _name: idp.document
        _description: IDP Document
    """

    _name = "idp.document"
    _description = "IDP Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    # Company and user fields for multi-tenant isolation
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Created By",
        default=lambda self: self.env.user,
        index=True,
    )

    # Core fields
    name = fields.Char(
        string="Document Name",
        compute="_compute_name",
        store=True,
        readonly=False,
    )
    file_path = fields.Char(
        string="File Path",
        help="Storage path for the document file",
    )
    file_hash = fields.Char(
        string="File Hash (SHA256)",
        help="Deduplication hash",
        index=True,
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Attachment",
        ondelete="set null",
        help="Link to Odoo attachment",
    )

    # Source metadata
    source = fields.Selection(
        [
            ("upload", "Manual Upload"),
            ("email", "Email Inbox"),
            ("api", "API"),
            ("mobile", "Mobile App"),
            ("drive", "Cloud Drive"),
        ],
        string="Source",
        default="upload",
        required=True,
        tracking=True,
    )
    source_reference = fields.Char(
        string="Source Reference",
        help="External reference ID (email ID, API request ID, etc.)",
    )

    # Document classification
    doc_type = fields.Selection(
        [
            ("invoice", "Invoice"),
            ("receipt", "Receipt"),
            ("purchase_order", "Purchase Order"),
            ("delivery_note", "Delivery Note"),
            ("unknown", "Unknown"),
        ],
        string="Document Type",
        default="unknown",
        tracking=True,
    )
    doc_type_confidence = fields.Float(
        string="Classification Confidence",
        help="Confidence score for document type classification (0.0-1.0)",
    )

    # Processing status
    status = fields.Selection(
        [
            ("queued", "Queued"),
            ("processing", "Processing"),
            ("classified", "Classified"),
            ("extracted", "Extracted"),
            ("validated", "Validated"),
            ("approved", "Auto-Approved"),
            ("review_needed", "Review Needed"),
            ("reviewed", "Reviewed"),
            ("exported", "Exported"),
            ("error", "Error"),
        ],
        string="Status",
        default="queued",
        required=True,
        tracking=True,
    )
    error_message = fields.Text(
        string="Error Message",
        help="Error details if processing failed",
    )

    # Processing timestamps
    queued_at = fields.Datetime(
        string="Queued At",
        default=fields.Datetime.now,
    )
    processed_at = fields.Datetime(
        string="Processed At",
    )
    exported_at = fields.Datetime(
        string="Exported At",
    )

    # Related records
    ocr_ids = fields.One2many(
        "idp.document.ocr",
        "document_id",
        string="OCR Results",
    )
    extraction_ids = fields.One2many(
        "idp.extraction",
        "document_id",
        string="Extractions",
    )
    review_ids = fields.One2many(
        "idp.review",
        "document_id",
        string="Reviews",
    )

    # Computed fields
    latest_extraction_id = fields.Many2one(
        "idp.extraction",
        string="Latest Extraction",
        compute="_compute_latest_extraction",
    )
    final_data = fields.Text(
        string="Final Extracted Data (JSON)",
        compute="_compute_final_data",
        help="The final approved/reviewed extraction data",
    )

    @api.depends("file_path", "attachment_id", "doc_type")
    def _compute_name(self):
        """Compute display name from file path or attachment."""
        for record in self:
            if record.attachment_id:
                record.name = record.attachment_id.name
            elif record.file_path:
                record.name = record.file_path.split("/")[-1]
            else:
                record.name = f"Document #{record.id or 'New'}"

    @api.depends("extraction_ids", "extraction_ids.create_date")
    def _compute_latest_extraction(self):
        """Get the most recent extraction for this document."""
        for record in self:
            extractions = record.extraction_ids.sorted("create_date", reverse=True)
            record.latest_extraction_id = extractions[0] if extractions else False

    @api.depends(
        "extraction_ids",
        "review_ids",
        "status",
    )
    def _compute_final_data(self):
        """
        Get final extracted data.

        Priority: reviewed correction > approved extraction > latest extraction
        """
        for record in self:
            # Check for reviewed corrections first
            reviewed = record.review_ids.filtered(lambda r: r.status == "approved")
            if reviewed:
                latest_review = reviewed.sorted("create_date", reverse=True)[0]
                record.final_data = latest_review.corrected_json
            elif record.latest_extraction_id:
                record.final_data = record.latest_extraction_id.extracted_json
            else:
                record.final_data = "{}"

    def action_process(self):
        """
        Trigger document processing.

        Runs the full IDP pipeline: OCR -> Classify -> Extract -> Validate.
        Uses async processing via queue_job if enabled.
        """
        params = self.env["ir.config_parameter"].sudo()
        async_enabled = params.get_param("ipai_idp.async_processing", "False") == "True"

        for record in self:
            if record.status not in ("queued", "error"):
                raise UserError(
                    _("Document must be in 'Queued' or 'Error' status to process.")
                )

            if async_enabled:
                record.action_queue_processing()
            else:
                record._run_idp_pipeline()

    def action_queue_processing(self):
        """
        Queue document for async processing via queue_job.

        If queue_job is not installed, falls back to synchronous processing.
        """
        for record in self:
            try:
                # Try to use queue_job if available
                record.with_delay(
                    description=f"IDP: Process {record.name}",
                    channel="root.idp",
                )._job_process_document()
                _logger.info("Document %s queued for async processing", record.id)
            except AttributeError:
                # queue_job not installed, fallback to sync
                _logger.warning(
                    "queue_job not available, processing document %s synchronously",
                    record.id,
                )
                record._run_idp_pipeline()

    def _job_process_document(self):
        """
        Job method for async document processing.

        Called by queue_job worker. Handles full pipeline with proper
        error handling and state management.
        """
        self.ensure_one()
        _logger.info("Starting async processing for document %s", self.id)

        try:
            self._run_idp_pipeline()
            _logger.info("Async processing completed for document %s", self.id)
        except Exception as e:
            _logger.exception("Async processing failed for document %s", self.id)
            # Error state is set in _run_idp_pipeline
            # Re-raise for queue_job retry logic
            raise

    def action_reprocess(self):
        """Reset and reprocess the document."""
        for record in self:
            record.write(
                {
                    "status": "queued",
                    "error_message": False,
                }
            )
            record.action_process()

    def action_approve(self):
        """Manually approve the extraction."""
        for record in self:
            if record.status not in ("extracted", "validated", "review_needed"):
                raise UserError(_("Document is not ready for approval."))
            record.write(
                {
                    "status": "approved",
                    "processed_at": fields.Datetime.now(),
                }
            )

    def action_request_review(self):
        """Flag document for human review."""
        for record in self:
            record.write({"status": "review_needed"})

    def action_export(self):
        """Export the document to downstream systems."""
        for record in self:
            if record.status not in ("approved", "reviewed"):
                raise UserError(_("Document must be approved before export."))
            # Placeholder for export logic
            record.write(
                {
                    "status": "exported",
                    "exported_at": fields.Datetime.now(),
                }
            )
            _logger.info("Document %s exported successfully", record.id)

    def _run_idp_pipeline(self):
        """
        Execute the full IDP processing pipeline.

        Steps:
        1. OCR (if needed)
        2. Classification
        3. LLM Extraction
        4. Validation
        5. Auto-approve or route to review
        """
        self.ensure_one()
        self.write({"status": "processing"})

        # Get configuration
        params = self.env["ir.config_parameter"].sudo()
        auto_approve_enabled = (
            params.get_param("ipai_idp.auto_approve_enabled", "True") == "True"
        )
        auto_approve_threshold = float(
            params.get_param("ipai_idp.auto_approve_confidence", "0.90")
        )

        try:
            # Step 1: OCR
            ocr_service = self.env["idp.service.ocr"]
            ocr_result = ocr_service.process_document(self)

            if not ocr_result:
                raise UserError(_("OCR processing failed."))

            # Step 2: Classification (from OCR or separate call)
            self.write({"status": "classified"})

            # Step 3: LLM Extraction
            extractor = self.env["idp.service.extractor"]
            extraction = extractor.extract(self, ocr_result)

            self.write({"status": "extracted"})

            # Step 4: Validation
            validator = self.env["idp.service.validator"]
            validation_result = validator.validate(extraction)

            if validation_result.get("status") == "pass":
                self.write({"status": "validated"})

                # Step 5: Auto-approve or route to review
                if (
                    auto_approve_enabled
                    and extraction.confidence >= auto_approve_threshold
                ):
                    self.write(
                        {
                            "status": "approved",
                            "processed_at": fields.Datetime.now(),
                        }
                    )
                    _logger.info(
                        "Document %s auto-approved (confidence: %.2f >= %.2f)",
                        self.id,
                        extraction.confidence,
                        auto_approve_threshold,
                    )
                else:
                    self.write({"status": "review_needed"})
                    _logger.info(
                        "Document %s needs review (confidence: %.2f < %.2f)",
                        self.id,
                        extraction.confidence,
                        auto_approve_threshold,
                    )
            else:
                self.write({"status": "review_needed"})
                _logger.info(
                    "Document %s needs review (validation: %s)",
                    self.id,
                    validation_result.get("status"),
                )

        except Exception as e:
            _logger.exception("IDP pipeline error for document %s", self.id)
            self.write(
                {
                    "status": "error",
                    "error_message": str(e),
                }
            )
            raise

    @api.model
    def compute_file_hash(self, file_content):
        """
        Compute SHA256 hash of file content for deduplication.

        Args:
            file_content: Binary file content

        Returns:
            str: SHA256 hex digest
        """
        return hashlib.sha256(file_content).hexdigest()

    @api.model
    def find_duplicate(self, file_hash):
        """
        Check if a document with the same hash already exists.

        Args:
            file_hash: SHA256 hash of the file

        Returns:
            idp.document or False
        """
        return self.search([("file_hash", "=", file_hash)], limit=1)
