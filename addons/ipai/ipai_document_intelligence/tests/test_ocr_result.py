# -*- coding: utf-8 -*-
from unittest.mock import patch

from odoo.tests import TransactionCase


class TestOcrResult(TransactionCase):
    """Tests for ipai.ocr.result model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['ir.config_parameter'].sudo().set_param(
            'ipai.doc_intelligence.auto_accept_threshold', '0.85'
        )
        cls.env['ir.config_parameter'].sudo().set_param(
            'ipai.doc_intelligence.reject_threshold', '0.3'
        )
        # Create a minimal job for linking
        cls.attachment = cls.env['ir.attachment'].create({
            'name': 'test_invoice.pdf',
            'datas': 'dGVzdA==',  # base64("test")
            'mimetype': 'application/pdf',
        })
        cls.job = cls.env['ipai.ai.job'].create({
            'job_type': 'ocr_extract',
            'source_model': 'account.move',
            'source_record_id': 1,
            'attachment_id': cls.attachment.id,
        })

    def _create_result(self, confidence=0.9, mode='prebuilt_invoice'):
        return self.env['ipai.ocr.result'].create({
            'job_id': self.job.id,
            'attachment_id': self.attachment.id,
            'extraction_mode': mode,
            'di_model_id': 'prebuilt-invoice',
            'page_count': 1,
            'raw_text': 'Invoice #123',
            'overall_confidence': confidence,
        })

    def test_review_auto_accept(self):
        """High confidence -> auto_accept."""
        result = self._create_result(confidence=0.95)
        self.assertEqual(result.review_recommendation, 'auto_accept')

    def test_review_needs_review(self):
        """Medium confidence -> review."""
        result = self._create_result(confidence=0.6)
        self.assertEqual(result.review_recommendation, 'review')

    def test_review_reject(self):
        """Low confidence -> reject."""
        result = self._create_result(confidence=0.2)
        self.assertEqual(result.review_recommendation, 'reject')

    def test_review_boundary_high(self):
        """Exactly at auto-accept threshold."""
        result = self._create_result(confidence=0.85)
        self.assertEqual(result.review_recommendation, 'auto_accept')

    def test_review_boundary_low(self):
        """Exactly at reject threshold."""
        result = self._create_result(confidence=0.3)
        self.assertEqual(result.review_recommendation, 'reject')

    def test_create_proposal_invoice(self):
        """Create proposal from invoice OCR result."""
        result = self._create_result(confidence=0.9)
        result.extracted_fields = {
            'VendorName': 'Test Vendor',
            'InvoiceId': 'INV-001',
            'InvoiceDate': '2026-03-20',
            'InvoiceTotal': {'amount': 1000.0, 'currencyCode': 'PHP'},
            'TotalTax': {'amount': 120.0},
        }
        action = result.action_create_proposal()
        self.assertEqual(action['res_model'], 'ipai.ai.proposal')
        proposal = self.env['ipai.ai.proposal'].browse(action['res_id'])
        self.assertEqual(proposal.vendor_name, 'Test Vendor')
        self.assertEqual(proposal.invoice_number, 'INV-001')
        self.assertAlmostEqual(proposal.total_amount, 1000.0)
        self.assertEqual(proposal.currency_code, 'PHP')

    def test_create_proposal_read_mode(self):
        """Create proposal from read-mode OCR (no invoice fields)."""
        result = self._create_result(confidence=0.8, mode='read')
        result.extracted_fields = {}
        action = result.action_create_proposal()
        proposal = self.env['ipai.ai.proposal'].browse(action['res_id'])
        self.assertEqual(proposal.proposal_type, 'suggest')

    def test_ocr_client_mode_mapping(self):
        """OCR client maps job types to DI models."""
        client = self.env['ipai.ocr.client']
        self.job.job_type = 'ocr_read'
        self.assertEqual(client._determine_mode(self.job), 'read')
        self.job.job_type = 'ocr_extract'
        self.assertEqual(client._determine_mode(self.job), 'prebuilt_invoice')
        self.job.job_type = 'finance_draft'
        self.assertEqual(client._determine_mode(self.job), 'prebuilt_invoice')
        self.job.job_type = 'finance_review'
        self.assertEqual(client._determine_mode(self.job), 'prebuilt_receipt')
