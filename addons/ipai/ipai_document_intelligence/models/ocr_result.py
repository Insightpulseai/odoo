# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class OcrResult(models.Model):
    """Normalized OCR extraction result.

    Stores output from Document Intelligence in a stable schema
    regardless of extraction mode (read/layout/prebuilt/custom).
    """

    _name = 'ipai.ocr.result'
    _description = 'OCR Extraction Result'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    # --- Link to AI job ---
    job_id = fields.Many2one('ipai.ai.job', required=True, ondelete='cascade', index=True)
    correlation_id = fields.Char(related='job_id.correlation_id', store=True)

    # --- Source ---
    attachment_id = fields.Many2one('ir.attachment', required=True, ondelete='restrict')
    attachment_name = fields.Char(related='attachment_id.name')
    source_model = fields.Char(related='job_id.source_model', store=True)
    source_record_id = fields.Integer(related='job_id.source_record_id', store=True)

    # --- Extraction mode ---
    extraction_mode = fields.Selection(
        [
            ('read', 'Read OCR'),
            ('layout', 'Layout Analysis'),
            ('prebuilt_invoice', 'Prebuilt Invoice'),
            ('prebuilt_receipt', 'Prebuilt Receipt'),
            ('prebuilt_id', 'Prebuilt ID Document'),
            ('custom', 'Custom Model'),
        ],
        required=True,
        default='read',
    )
    di_model_id = fields.Char(string='DI Model ID')
    di_api_version = fields.Char()

    # --- Normalized output ---
    page_count = fields.Integer()
    raw_text = fields.Text()
    text_blocks = fields.Json()
    tables = fields.Json()
    key_value_pairs = fields.Json()
    extracted_fields = fields.Json()

    # --- Confidence and review ---
    overall_confidence = fields.Float(digits=(3, 2))
    field_confidences = fields.Json()
    review_recommendation = fields.Selection(
        [
            ('auto_accept', 'Auto-Accept'),
            ('review', 'Human Review'),
            ('reject', 'Reject / Re-scan'),
        ],
        compute='_compute_review_recommendation',
        store=True,
    )

    # --- Processing metadata ---
    processing_time_ms = fields.Integer()
    di_operation_id = fields.Char(string='DI Operation ID')
    processed_at = fields.Datetime()
    error_message = fields.Text()

    @api.depends('overall_confidence')
    def _compute_review_recommendation(self):
        high_threshold = float(
            self.env['ir.config_parameter'].sudo().get_param(
                'ipai.doc_intelligence.auto_accept_threshold', '0.85'
            )
        )
        low_threshold = float(
            self.env['ir.config_parameter'].sudo().get_param(
                'ipai.doc_intelligence.reject_threshold', '0.3'
            )
        )
        for rec in self:
            if rec.overall_confidence >= high_threshold:
                rec.review_recommendation = 'auto_accept'
            elif rec.overall_confidence <= low_threshold:
                rec.review_recommendation = 'reject'
            else:
                rec.review_recommendation = 'review'

    def action_create_proposal(self):
        """Create an AI proposal from this OCR result for human review."""
        self.ensure_one()
        proposal_vals = {
            'job_id': self.job_id.id,
            'target_model': self.source_model or 'account.move',
            'target_record_id': self.source_record_id,
            'proposal_type': 'draft_entry' if self.extraction_mode in (
                'prebuilt_invoice', 'prebuilt_receipt'
            ) else 'suggest',
            'proposed_values': self.extracted_fields or {},
            'proposed_summary': _('OCR extraction from %s (%d pages, %.0f%% confidence)',
                                  self.attachment_name, self.page_count or 0,
                                  (self.overall_confidence or 0) * 100),
        }
        # Map invoice-specific fields
        if self.extracted_fields:
            ef = self.extracted_fields
            proposal_vals.update({
                'vendor_name': ef.get('VendorName', ''),
                'invoice_number': ef.get('InvoiceId', ''),
                'invoice_date': ef.get('InvoiceDate'),
                'total_amount': ef.get('InvoiceTotal', {}).get('amount', 0),
                'currency_code': ef.get('InvoiceTotal', {}).get('currencyCode', ''),
                'tax_amount': ef.get('TotalTax', {}).get('amount', 0),
            })
        proposal = self.env['ipai.ai.proposal'].create(proposal_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ipai.ai.proposal',
            'res_id': proposal.id,
            'view_mode': 'form',
        }
