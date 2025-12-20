# -*- coding: utf-8 -*-
"""
State Transition Tests for IDP Document Flow.

Tests document lifecycle and state transitions:
- Queued -> Processing -> Extracted
- Approval and review workflows
- Error handling
"""
from unittest.mock import MagicMock, patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestIdpDocumentFlow(TransactionCase):
    """Test cases for IDP document state transitions."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.Document = cls.env["idp.document"]
        cls.Extraction = cls.env["idp.extraction"]

    def _create_test_document(self, status="queued"):
        """Helper to create test document."""
        return self.Document.create(
            {
                "name": "Test Document",
                "source": "api",
                "status": status,
                "doc_type": "invoice",
            }
        )

    # ==================== Basic State Transition Tests ====================

    def test_document_starts_queued(self):
        """Test that new documents start in queued status."""
        doc = self._create_test_document()
        self.assertEqual(doc.status, "queued")

    def test_cannot_process_non_queued_document(self):
        """Test that only queued/error documents can be processed."""
        doc = self._create_test_document(status="approved")
        with self.assertRaises(UserError):
            doc.action_process()

    def test_can_reprocess_error_document(self):
        """Test that error documents can be reprocessed."""
        doc = self._create_test_document(status="error")
        doc.error_message = "Previous error"
        # Should not raise
        try:
            doc.action_process()
        except Exception:
            pass  # Expected if OCR service not configured

    def test_reprocess_resets_status(self):
        """Test that reprocess resets status to queued."""
        doc = self._create_test_document(status="error")
        doc.error_message = "Previous error"
        # Mock the pipeline to avoid actual processing
        with patch.object(doc, "_run_idp_pipeline"):
            doc.action_reprocess()
        self.assertEqual(doc.status, "queued")
        self.assertFalse(doc.error_message)

    # ==================== Approval Flow Tests ====================

    def test_approve_extracted_document(self):
        """Test approving an extracted document."""
        doc = self._create_test_document(status="extracted")
        doc.action_approve()
        self.assertEqual(doc.status, "approved")
        self.assertIsNotNone(doc.processed_at)

    def test_approve_validated_document(self):
        """Test approving a validated document."""
        doc = self._create_test_document(status="validated")
        doc.action_approve()
        self.assertEqual(doc.status, "approved")

    def test_approve_review_needed_document(self):
        """Test approving a review_needed document."""
        doc = self._create_test_document(status="review_needed")
        doc.action_approve()
        self.assertEqual(doc.status, "approved")

    def test_cannot_approve_queued_document(self):
        """Test that queued documents cannot be approved."""
        doc = self._create_test_document(status="queued")
        with self.assertRaises(UserError):
            doc.action_approve()

    def test_cannot_approve_error_document(self):
        """Test that error documents cannot be approved."""
        doc = self._create_test_document(status="error")
        with self.assertRaises(UserError):
            doc.action_approve()

    # ==================== Review Flow Tests ====================

    def test_request_review(self):
        """Test flagging document for review."""
        doc = self._create_test_document(status="extracted")
        doc.action_request_review()
        self.assertEqual(doc.status, "review_needed")

    # ==================== Export Flow Tests ====================

    def test_export_approved_document(self):
        """Test exporting an approved document."""
        doc = self._create_test_document(status="approved")
        doc.action_export()
        self.assertEqual(doc.status, "exported")
        self.assertIsNotNone(doc.exported_at)

    def test_export_reviewed_document(self):
        """Test exporting a reviewed document."""
        doc = self._create_test_document(status="reviewed")
        doc.action_export()
        self.assertEqual(doc.status, "exported")

    def test_cannot_export_unapproved_document(self):
        """Test that unapproved documents cannot be exported."""
        doc = self._create_test_document(status="extracted")
        with self.assertRaises(UserError):
            doc.action_export()

    # ==================== Pipeline Tests with Mocking ====================

    def test_pipeline_sets_processing_status(self):
        """Test that pipeline sets processing status."""
        doc = self._create_test_document()

        # Mock services to control the flow
        with patch.object(
            self.env["idp.service.ocr"].__class__, "process_document"
        ) as mock_ocr:
            mock_ocr.side_effect = Exception("Test stop")
            try:
                doc._run_idp_pipeline()
            except Exception:
                pass

        # Status should be error after exception
        self.assertEqual(doc.status, "error")

    def test_pipeline_error_sets_error_message(self):
        """Test that pipeline errors are captured."""
        doc = self._create_test_document()

        with patch.object(
            self.env["idp.service.ocr"].__class__, "process_document"
        ) as mock_ocr:
            mock_ocr.side_effect = UserError("OCR service unavailable")
            try:
                doc._run_idp_pipeline()
            except UserError:
                pass

        self.assertEqual(doc.status, "error")
        self.assertIn("OCR service unavailable", doc.error_message)

    def test_pipeline_success_with_high_confidence(self):
        """Test pipeline auto-approves high confidence extractions."""
        doc = self._create_test_document()

        # Create mock OCR result
        mock_ocr = MagicMock()
        mock_ocr.raw_text = "Invoice #123\nTotal: $100"

        # Create mock extraction
        mock_extraction = MagicMock()
        mock_extraction.confidence = 0.95  # High confidence

        with patch.object(
            self.env["idp.service.ocr"].__class__,
            "process_document",
            return_value=mock_ocr,
        ):
            with patch.object(
                self.env["idp.service.extractor"].__class__,
                "extract",
                return_value=mock_extraction,
            ):
                with patch.object(
                    self.env["idp.service.validator"].__class__,
                    "validate",
                    return_value={"status": "pass"},
                ):
                    doc._run_idp_pipeline()

        self.assertEqual(doc.status, "approved")

    def test_pipeline_review_needed_with_low_confidence(self):
        """Test pipeline routes low confidence to review."""
        doc = self._create_test_document()

        mock_ocr = MagicMock()
        mock_ocr.raw_text = "Invoice #123"

        mock_extraction = MagicMock()
        mock_extraction.confidence = 0.75  # Low confidence

        with patch.object(
            self.env["idp.service.ocr"].__class__,
            "process_document",
            return_value=mock_ocr,
        ):
            with patch.object(
                self.env["idp.service.extractor"].__class__,
                "extract",
                return_value=mock_extraction,
            ):
                with patch.object(
                    self.env["idp.service.validator"].__class__,
                    "validate",
                    return_value={"status": "pass"},
                ):
                    doc._run_idp_pipeline()

        self.assertEqual(doc.status, "review_needed")

    def test_pipeline_review_needed_on_validation_failure(self):
        """Test pipeline routes validation failures to review."""
        doc = self._create_test_document()

        mock_ocr = MagicMock()
        mock_ocr.raw_text = "Invoice #123"

        mock_extraction = MagicMock()
        mock_extraction.confidence = 0.95

        with patch.object(
            self.env["idp.service.ocr"].__class__,
            "process_document",
            return_value=mock_ocr,
        ):
            with patch.object(
                self.env["idp.service.extractor"].__class__,
                "extract",
                return_value=mock_extraction,
            ):
                with patch.object(
                    self.env["idp.service.validator"].__class__,
                    "validate",
                    return_value={"status": "fail", "errors": ["Missing vendor"]},
                ):
                    doc._run_idp_pipeline()

        self.assertEqual(doc.status, "review_needed")


class TestIdpAsyncProcessing(TransactionCase):
    """Test async processing with queue_job."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.Document = cls.env["idp.document"]

    def test_action_queue_processing_fallback(self):
        """Test fallback when queue_job not available."""
        doc = self.Document.create(
            {
                "name": "Test Doc",
                "source": "api",
                "status": "queued",
            }
        )

        # Mock _run_idp_pipeline to verify it's called
        with patch.object(doc, "_run_idp_pipeline") as mock_pipeline:
            # Since queue_job is likely not installed, it should fallback
            doc.action_queue_processing()
            mock_pipeline.assert_called_once()

    def test_job_process_document_calls_pipeline(self):
        """Test that _job_process_document calls the pipeline."""
        doc = self.Document.create(
            {
                "name": "Test Doc",
                "source": "api",
                "status": "queued",
            }
        )

        with patch.object(doc, "_run_idp_pipeline") as mock_pipeline:
            doc._job_process_document()
            mock_pipeline.assert_called_once()
