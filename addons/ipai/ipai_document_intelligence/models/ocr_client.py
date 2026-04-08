# -*- coding: utf-8 -*-
"""Azure Document Intelligence client service.

Handles async OCR submission, polling, and result normalization.
Secrets resolved at runtime via env vars or ipai.doc.digitization.config.
"""
import base64
import logging
import os
import time

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

SUPPORTED_MIMETYPES = {
    'application/pdf', 'image/png', 'image/jpeg', 'image/tiff', 'image/bmp',
}

MODEL_MAP = {
    'read': 'prebuilt-read',
    'layout': 'prebuilt-layout',
    'prebuilt_invoice': 'prebuilt-invoice',
    'prebuilt_receipt': 'prebuilt-receipt',
    'prebuilt_id': 'prebuilt-idDocument',
}


class OcrClientService(models.AbstractModel):
    """Service model for Azure Document Intelligence operations."""

    _name = 'ipai.ocr.client'
    _description = 'Document Intelligence Client'

    def submit_ocr_job(self, job):
        """Submit an OCR job to Document Intelligence.

        Args:
            job: ipai.ai.job record with attachment_id set.

        Returns:
            ipai.ocr.result record.
        """
        job.action_start()

        attachment = job.attachment_id
        if not attachment:
            job.action_fail('No attachment linked to job.', 'data')
            raise UserError(_('No attachment linked to OCR job.'))

        if attachment.mimetype not in SUPPORTED_MIMETYPES:
            job.action_fail(
                _('Unsupported file type: %s', attachment.mimetype), 'data'
            )
            raise UserError(_('Unsupported file type for OCR: %s', attachment.mimetype))

        config = self._get_config()
        if not config:
            job.action_fail('Document Intelligence not configured.', 'auth')
            raise UserError(_('Document Intelligence is not configured.'))

        extraction_mode = self._determine_mode(job)
        model_id = MODEL_MAP.get(extraction_mode, 'prebuilt-read')

        try:
            endpoint = config.endpoint.rstrip('/')
            api_key = os.getenv('AZURE_DI_API_KEY') or os.getenv('AZURE_DOC_INTEL_KEY', '')
            if not api_key:
                job.action_fail('Missing env var AZURE_DI_API_KEY.', 'auth')
                return None

            api_version = self.env['ir.config_parameter'].sudo().get_param(
                'ipai.doc_intelligence.api_version', '2024-11-30'
            )
            url = (
                f"{endpoint}/documentintelligence/documentModels/{model_id}"
                f":analyze?api-version={api_version}"
            )
            headers = {
                'Ocp-Apim-Subscription-Key': api_key,
                'Content-Type': attachment.mimetype,
            }
            file_data = base64.b64decode(attachment.datas)

            resp = requests.post(url, headers=headers, data=file_data, timeout=30)
            resp.raise_for_status()

            operation_url = resp.headers.get('Operation-Location')
            if not operation_url:
                job.action_fail('No Operation-Location in DI response.', 'service')
                return None

            result_data = self._poll_result(operation_url, api_key)
            ocr_result = self._normalize_result(job, result_data, extraction_mode, model_id)

            confidence = ocr_result.overall_confidence
            job.write({
                'external_job_id': ocr_result.di_operation_id,
                'model_name': model_id,
                'model_version': api_version,
            })
            job.action_complete(
                result_payload={'ocr_result_id': ocr_result.id},
                confidence=confidence,
            )
            return ocr_result

        except requests.exceptions.Timeout:
            job.action_fail('Document Intelligence request timed out.', 'timeout')
        except requests.exceptions.ConnectionError as e:
            job.action_fail(_('Connection error: %s', str(e)), 'network')
        except requests.exceptions.HTTPError as e:
            job.action_fail(_('HTTP error: %s', str(e)), 'service')
        except Exception as e:
            _logger.exception('OCR job %s failed unexpectedly', job.correlation_id)
            job.action_fail(_('Unexpected error: %s', str(e)), 'service')
        return None

    def _get_config(self):
        """Get Document Intelligence configuration singleton."""
        return self.env['ipai.doc.digitization.config'].search([], limit=1)

    def _determine_mode(self, job):
        """Determine extraction mode based on job type and config."""
        mode_map = {
            'ocr_read': 'read',
            'ocr_extract': 'prebuilt_invoice',
            'ocr_classify': 'layout',
            'finance_draft': 'prebuilt_invoice',
            'finance_review': 'prebuilt_receipt',
        }
        return mode_map.get(job.job_type, 'read')

    def _poll_result(self, operation_url, api_key, max_attempts=30, interval=2):
        """Poll DI operation until complete or timeout."""
        headers = {'Ocp-Apim-Subscription-Key': api_key}
        for attempt in range(max_attempts):
            resp = requests.get(operation_url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            status = data.get('status', '')
            if status == 'succeeded':
                return data.get('analyzeResult', {})
            if status == 'failed':
                error = data.get('error', {}).get('message', 'Unknown DI error')
                raise UserError(_('Document Intelligence failed: %s', error))
            time.sleep(interval)
        raise UserError(_('Document Intelligence timed out after %d attempts.', max_attempts))

    def _normalize_result(self, job, result_data, extraction_mode, model_id):
        """Normalize DI output into ipai.ocr.result record."""
        pages = result_data.get('pages', [])
        content = result_data.get('content', '')
        tables = result_data.get('tables', [])
        kv_pairs = result_data.get('keyValuePairs', [])
        documents = result_data.get('documents', [])

        # Extract fields from first document if present
        extracted_fields = {}
        field_confidences = {}
        if documents:
            doc = documents[0]
            for field_name, field_data in doc.get('fields', {}).items():
                extracted_fields[field_name] = field_data.get('valueString',
                    field_data.get('valueNumber',
                    field_data.get('valueDate',
                    field_data.get('content', ''))))
                if isinstance(field_data.get('value'), dict):
                    extracted_fields[field_name] = field_data['value']
                field_confidences[field_name] = field_data.get('confidence', 0)

        # Compute overall confidence
        confidences = list(field_confidences.values()) if field_confidences else [
            p.get('confidence', 0) for p in pages if 'confidence' in p
        ]
        overall = sum(confidences) / len(confidences) if confidences else 0.0

        return self.env['ipai.ocr.result'].create({
            'job_id': job.id,
            'attachment_id': job.attachment_id.id,
            'extraction_mode': extraction_mode,
            'di_model_id': model_id,
            'di_api_version': result_data.get('apiVersion', ''),
            'page_count': len(pages),
            'raw_text': content,
            'text_blocks': [
                {'page': p.get('pageNumber'), 'lines': [
                    l.get('content', '') for l in p.get('lines', [])
                ]} for p in pages
            ],
            'tables': [
                {
                    'row_count': t.get('rowCount', 0),
                    'column_count': t.get('columnCount', 0),
                    'cells': [
                        {
                            'row': c.get('rowIndex'),
                            'col': c.get('columnIndex'),
                            'content': c.get('content', ''),
                        } for c in t.get('cells', [])
                    ],
                } for t in tables
            ],
            'key_value_pairs': [
                {
                    'key': kv.get('key', {}).get('content', ''),
                    'value': kv.get('value', {}).get('content', ''),
                    'confidence': kv.get('confidence', 0),
                } for kv in kv_pairs
            ],
            'extracted_fields': extracted_fields,
            'overall_confidence': overall,
            'field_confidences': field_confidences,
            'processed_at': fields.Datetime.now(),
        })
