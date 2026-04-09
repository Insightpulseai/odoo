# -*- coding: utf-8 -*-
import base64
import hashlib
import io
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

SOURCE_TYPES = [
    ('pdf', 'PDF'),
    ('image', 'Image'),
    ('docx', 'Word Document'),
    ('xlsx', 'Excel Spreadsheet'),
    ('url', 'Web URL'),
]

SOURCE_STATUSES = [
    ('draft', 'Draft'),
    ('processing', 'Processing'),
    ('indexed', 'Indexed'),
    ('failed', 'Failed'),
]

# Valid state transitions: from -> allowed to
_TRANSITIONS = {
    'draft': {'processing'},
    'processing': {'indexed', 'failed'},
    'failed': {'processing'},
    'indexed': set(),
}

MIME_TO_TYPE = {
    'application/pdf': 'pdf',
    'image/png': 'image',
    'image/jpeg': 'image',
    'image/webp': 'image',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
}


class ChatSource(models.Model):
    _name = 'ipai.chat.source'
    _description = 'Chat Source'
    _order = 'create_date desc, id desc'

    name = fields.Char(
        string='Name',
        required=True,
    )
    session_id = fields.Many2one(
        'ipai.chat.session',
        string='Session',
        required=True,
        index=True,
        ondelete='cascade',
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
        index=True,
        ondelete='set null',
    )
    source_type = fields.Selection(
        SOURCE_TYPES,
        string='Type',
        required=True,
        index=True,
    )
    status = fields.Selection(
        SOURCE_STATUSES,
        string='Status',
        default='draft',
        required=True,
        index=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        index=True,
    )
    url = fields.Char(
        string='URL',
        help='Source URL for url-type sources',
    )
    external_source_id = fields.Char(
        string='External Source ID',
        readonly=True,
        copy=False,
        index=True,
    )
    external_index_id = fields.Char(
        string='External Index ID',
        readonly=True,
        copy=False,
    )
    last_error = fields.Text(
        string='Last Error',
        readonly=True,
    )
    processed_at = fields.Datetime(
        string='Processed At',
        readonly=True,
    )
    checksum = fields.Char(
        string='Checksum (SHA-256)',
        index=True,
        readonly=True,
        copy=False,
    )
    file_size = fields.Integer(
        string='File Size',
        readonly=True,
    )
    company_id = fields.Many2one(
        related='session_id.company_id',
        store=True,
        index=True,
    )

    # --- Extraction results ---
    extracted_text = fields.Text(
        string='Extracted Text',
        readonly=True,
    )
    extraction_method = fields.Char(
        string='Extraction Method',
        readonly=True,
        help='How text was extracted: pdf, docx, xlsx, direct, ocr, doc_intelligence',
    )
    token_estimate = fields.Integer(
        string='Token Estimate',
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('attachment_id') and not vals.get('checksum'):
                att = self.env['ir.attachment'].browse(vals['attachment_id'])
                if att.datas:
                    import base64
                    raw = base64.b64decode(att.datas)
                    vals['checksum'] = hashlib.sha256(raw).hexdigest()
                    vals.setdefault('file_size', len(raw))
        return super().create(vals_list)

    def _set_status(self, new_status, error=None, **kwargs):
        """Transition source to a new status with validation."""
        for rec in self:
            allowed = _TRANSITIONS.get(rec.status, set())
            if new_status not in allowed:
                raise UserError(
                    f'Cannot transition source "{rec.name}" '
                    f'from {rec.status} to {new_status}.'
                )
            vals = {'status': new_status, 'last_error': error}
            vals.update(kwargs)
            rec.write(vals)

    def action_submit_for_processing(self):
        """Move draft source to processing and run local extraction."""
        for rec in self:
            rec._set_status('processing')
            rec._run_local_extraction()

    def action_retry(self):
        """Retry a failed source by moving it back to processing."""
        for rec in self:
            if rec.status != 'failed':
                raise UserError('Only failed sources can be retried.')
            rec._set_status('processing', error=False)
            rec._run_local_extraction()

    def action_deactivate(self):
        self.write({'active': False})

    def action_activate(self):
        self.write({'active': True})

    def is_eligible(self):
        """Check if this source can be used for grounded chat."""
        self.ensure_one()
        return self.active and self.status == 'indexed'

    # ------------------------------------------------------------------
    # Local extraction
    # ------------------------------------------------------------------

    def _run_local_extraction(self):
        """Extract text from the source attachment locally.

        On success: status → indexed, extracted_text populated.
        On failure: status → failed, last_error populated.
        """
        self.ensure_one()
        if self.status != 'processing':
            return

        if self.source_type == 'url':
            # URL extraction requires external fetch — skip local
            self._set_status(
                'failed',
                error='URL source extraction requires agent-platform.',
            )
            return

        if not self.attachment_id or not self.attachment_id.datas:
            self._set_status('failed', error='No attachment data available.')
            return

        try:
            raw = base64.b64decode(self.attachment_id.datas)
            text, method = self._extract_text(raw)
            if text and text.strip():
                self._set_status(
                    'indexed',
                    extracted_text=text,
                    extraction_method=method,
                    token_estimate=len(text) // 4,
                    processed_at=fields.Datetime.now(),
                )
            else:
                self._set_status(
                    'failed',
                    error=f'No text could be extracted (method: {method}).',
                )
        except Exception as e:
            _logger.warning('Local extraction failed for source %d: %s', self.id, e)
            self._set_status('failed', error=str(e)[:500])

    def _extract_text(self, raw):
        """Dispatch extraction by source_type. Returns (text, method)."""
        self.ensure_one()
        if self.source_type == 'pdf':
            return self._extract_pdf(raw)
        elif self.source_type == 'docx':
            return self._extract_docx(raw)
        elif self.source_type == 'xlsx':
            return self._extract_xlsx(raw)
        elif self.source_type == 'image':
            return self._extract_image(raw)
        return '', 'unsupported'

    def _extract_pdf(self, raw):
        """Extract text from PDF. PyPDF2 first, then Doc Intelligence."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(raw))
            pages = []
            for page in reader.pages[:50]:
                text = page.extract_text()
                if text and text.strip():
                    pages.append(text)
            if pages:
                return '\n\n'.join(pages), 'pdf'
        except ImportError:
            _logger.debug('PyPDF2 not available, trying Doc Intelligence')
        except Exception as e:
            _logger.debug('PyPDF2 extraction failed: %s', e)

        # Fallback to Document Intelligence
        return self._extract_via_doc_intelligence('prebuilt-read')

    def _extract_docx(self, raw):
        """Extract text from DOCX via ZIP/XML parsing."""
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            zf = zipfile.ZipFile(io.BytesIO(raw))
            xml_content = zf.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            paragraphs = []
            for p in tree.iter(f'{{{ns}}}p'):
                texts = [
                    t.text for t in p.iter(f'{{{ns}}}t')
                    if t.text
                ]
                if texts:
                    paragraphs.append(''.join(texts))
            return '\n'.join(paragraphs), 'docx'
        except Exception as e:
            _logger.warning('DOCX extraction failed: %s', e)
            return '', 'docx_error'

    def _extract_xlsx(self, raw):
        """Extract text from XLSX as CSV-like rows."""
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            zf = zipfile.ZipFile(io.BytesIO(raw))
            shared_strings = []
            if 'xl/sharedStrings.xml' in zf.namelist():
                ss_xml = zf.read('xl/sharedStrings.xml')
                ss_tree = ET.fromstring(ss_xml)
                ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
                for si in ss_tree.iter(f'{{{ns}}}si'):
                    texts = [t.text or '' for t in si.iter(f'{{{ns}}}t')]
                    shared_strings.append(''.join(texts))
            sheet_xml = zf.read('xl/worksheets/sheet1.xml')
            sheet_tree = ET.fromstring(sheet_xml)
            ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
            rows = []
            for row in list(sheet_tree.iter(f'{{{ns}}}row'))[:200]:
                cells = []
                for cell in row.iter(f'{{{ns}}}c'):
                    val_el = cell.find(f'{{{ns}}}v')
                    val = val_el.text if val_el is not None else ''
                    if cell.get('t') == 's' and val:
                        idx = int(val)
                        val = shared_strings[idx] if idx < len(shared_strings) else val
                    cells.append(val or '')
                rows.append(','.join(cells))
            return '\n'.join(rows), 'xlsx'
        except Exception as e:
            _logger.warning('XLSX extraction failed: %s', e)
            return '', 'xlsx_error'

    def _extract_image(self, raw):
        """Extract text from image via local OCR then Doc Intelligence."""
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(io.BytesIO(raw))
            text = pytesseract.image_to_string(img, lang='eng')
            if text and text.strip():
                return text.strip(), 'image_ocr_local'
        except Exception as e:
            _logger.debug('Local image OCR failed: %s', e)
        return self._extract_via_doc_intelligence('prebuilt-read')

    def _extract_via_doc_intelligence(self, model_id):
        """Fallback to Azure Document Intelligence for extraction."""
        self.ensure_one()
        try:
            svc = self.env['ipai.doc.intelligence.service']
            result = svc.analyze_document(
                self.attachment_id.id, model_id=model_id,
            )
            if result.get('status') == 'success':
                content = result.get('result', {}).get('content', '')
                return content, 'doc_intelligence'
        except Exception as e:
            _logger.warning('Doc Intelligence extraction failed: %s', e)
        return '', 'extraction_unavailable'

    # ------------------------------------------------------------------
    # Callback (from agent-platform)
    # ------------------------------------------------------------------

    def apply_callback(self, payload):
        """Apply status update from external ingestion callback.

        Expected payload keys:
            status: 'indexed' or 'failed'
            external_source_id: str (optional)
            external_index_id: str (optional)
            error: str or None
            processed_at: ISO datetime string (optional)
        """
        self.ensure_one()
        new_status = payload.get('status')
        if new_status not in ('indexed', 'failed'):
            raise UserError(
                f'Invalid callback status: {new_status}'
            )
        update_vals = {}
        if payload.get('external_source_id'):
            update_vals['external_source_id'] = payload['external_source_id']
        if payload.get('external_index_id'):
            update_vals['external_index_id'] = payload['external_index_id']
        if payload.get('processed_at'):
            update_vals['processed_at'] = payload['processed_at']
        self._set_status(
            new_status,
            error=payload.get('error'),
            **update_vals,
        )
