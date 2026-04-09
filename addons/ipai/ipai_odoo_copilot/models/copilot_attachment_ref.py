# -*- coding: utf-8 -*-

import hashlib
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Allowed MIME types for copilot attachments
_ALLOWED_MIMETYPES = frozenset({
    'text/plain',
    'text/markdown',
    'text/csv',
    'application/json',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'image/png',
    'image/jpeg',
    'image/webp',
})

# Maximum file size in bytes (10 MB)
_MAX_FILE_SIZE = 10 * 1024 * 1024

# Maximum attachments per message
_MAX_ATTACHMENTS_PER_MESSAGE = 5


class CopilotAttachmentRef(models.Model):
    """Copilot attachment reference — metadata layer over ir.attachment.

    Separates copilot-specific state (ingestion, extraction, token estimate)
    from the canonical ir.attachment record. Odoo owns the file via
    ir.attachment; this model owns the copilot lifecycle.
    """
    _name = 'ipai.copilot.attachment.ref'
    _description = 'Copilot Attachment Reference'
    _order = 'create_date desc, id desc'

    # --- Core references ---
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
        required=True,
        ondelete='cascade',
        index=True,
    )
    message_id = fields.Many2one(
        'ipai.copilot.message',
        string='Message',
        ondelete='set null',
        index=True,
    )
    conversation_id = fields.Many2one(
        'ipai.copilot.conversation',
        string='Conversation',
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )

    # --- File metadata (denormalized from ir.attachment for fast access) ---
    filename = fields.Char(required=True)
    mime_type = fields.Char(required=True)
    file_size = fields.Integer()
    content_sha256 = fields.Char(
        string='Content SHA256',
        index=True,
        help='Dedup and integrity check',
    )

    # --- Ingestion pipeline state ---
    ingestion_state = fields.Selection(
        [
            ('pending', 'Pending'),
            ('extracting', 'Extracting'),
            ('done', 'Done'),
            ('skip', 'Skipped'),
            ('error', 'Error'),
        ],
        default='pending',
        required=True,
        index=True,
    )
    extracted_text = fields.Text(
        help='Normalized plain text extracted from the file',
    )
    extraction_method = fields.Char(
        help='Method used: direct, pdf, docx, ocr, doc_intelligence',
    )
    token_estimate = fields.Integer(
        help='Approximate token count of extracted text',
    )
    extraction_error = fields.Text()

    # --- Origin tracking ---
    origin = fields.Selection(
        [
            ('upload', 'User Upload'),
            ('existing', 'Existing Odoo Document'),
        ],
        default='upload',
        required=True,
    )
    source_model = fields.Char(
        help='If origin=existing, the model the attachment came from',
    )
    source_res_id = fields.Integer(
        help='If origin=existing, the record ID the attachment came from',
    )

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('content_sha256') and vals.get('attachment_id'):
                att = self.env['ir.attachment'].browse(vals['attachment_id'])
                if att.exists() and att.datas:
                    import base64
                    raw = base64.b64decode(att.datas)
                    vals['content_sha256'] = hashlib.sha256(raw).hexdigest()
                    if not vals.get('file_size'):
                        vals['file_size'] = len(raw)
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Ingestion
    # -------------------------------------------------------------------------

    def run_extraction(self):
        """Run text extraction based on mime type.

        Dispatches to the appropriate extractor. Updates ingestion_state
        and extracted_text on completion.
        """
        for ref in self:
            if ref.ingestion_state not in ('pending', 'error'):
                continue
            ref.ingestion_state = 'extracting'
            try:
                text, method = ref._extract_text()
                ref.write({
                    'extracted_text': text,
                    'extraction_method': method,
                    'ingestion_state': 'done' if text else 'skip',
                    'token_estimate': ref._estimate_tokens(text),
                    'extraction_error': False,
                })
            except Exception as e:
                _logger.warning(
                    'Extraction failed for ref %d: %s', ref.id, e,
                )
                ref.write({
                    'ingestion_state': 'error',
                    'extraction_error': str(e)[:500],
                })

    def _extract_text(self):
        """Extract text from the underlying ir.attachment.

        Returns (text, method) tuple.
        """
        self.ensure_one()
        import base64
        att = self.attachment_id
        if not att.datas:
            return '', 'empty'

        raw = base64.b64decode(att.datas)
        mime = self.mime_type or ''

        # Direct text formats
        if mime in ('text/plain', 'text/markdown', 'text/csv'):
            return raw.decode('utf-8', errors='replace'), 'direct'

        if mime == 'application/json':
            return raw.decode('utf-8', errors='replace'), 'direct'

        # PDF extraction
        if mime == 'application/pdf':
            return self._extract_pdf(raw)

        # DOCX extraction
        if mime == (
            'application/vnd.openxmlformats-officedocument'
            '.wordprocessingml.document'
        ):
            return self._extract_docx(raw)

        # XLSX — extract as CSV-like text
        if mime == (
            'application/vnd.openxmlformats-officedocument'
            '.spreadsheetml.sheet'
        ):
            return self._extract_xlsx(raw)

        # Images — try Document Intelligence OCR if configured
        if mime.startswith('image/'):
            return self._extract_image_ocr()

        return '', 'unsupported'

    def _extract_pdf(self, raw):
        """Extract text from PDF bytes.

        Strategy:
          1. PyPDF2 text extraction (fast, for text-layer PDFs)
          2. Local OCR via pytesseract + pdf2image (for scanned PDFs)
          3. Azure Document Intelligence (remote fallback)
        """
        import io

        # 1. Try PyPDF2 first (fast, text-layer PDFs)
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
            pass
        except Exception as e:
            _logger.debug('PyPDF2 extraction failed: %s', e)

        # 2. Local OCR fallback (scanned PDFs)
        try:
            text = self._extract_pdf_ocr_local(raw)
            if text and text.strip():
                return text, 'pdf_ocr_local'
        except Exception as e:
            _logger.debug('Local PDF OCR failed: %s', e)

        # 3. Azure Document Intelligence (remote)
        return self._extract_via_doc_intelligence('prebuilt-read')

    def _extract_pdf_ocr_local(self, raw):
        """OCR a scanned PDF locally via pytesseract + pdf2image."""
        from pdf2image import convert_from_bytes
        import pytesseract

        images = convert_from_bytes(
            raw, first_page=1, last_page=20, dpi=300,
        )
        pages = []
        for img in images:
            # Grayscale for better OCR accuracy
            gray = img.convert('L')
            # psm 3 = fully automatic page segmentation (best for invoices)
            text = pytesseract.image_to_string(gray, lang='eng')
            if text and text.strip():
                pages.append(text.strip())
        return '\n\n'.join(pages)

    def _extract_docx(self, raw):
        """Extract text from DOCX bytes."""
        try:
            import io
            import zipfile
            import xml.etree.ElementTree as ET
            zf = zipfile.ZipFile(io.BytesIO(raw))
            xml_content = zf.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = []
            for p in tree.iter('{%s}p' % ns['w']):
                texts = [
                    t.text for t in p.iter('{%s}t' % ns['w'])
                    if t.text
                ]
                if texts:
                    paragraphs.append(''.join(texts))
            return '\n'.join(paragraphs), 'docx'
        except Exception as e:
            _logger.warning('DOCX extraction failed: %s', e)
            return '', 'docx_error'

    def _extract_xlsx(self, raw):
        """Extract text from XLSX as CSV-like representation."""
        try:
            import io
            import zipfile
            import xml.etree.ElementTree as ET
            zf = zipfile.ZipFile(io.BytesIO(raw))
            # Read shared strings
            shared_strings = []
            if 'xl/sharedStrings.xml' in zf.namelist():
                ss_xml = zf.read('xl/sharedStrings.xml')
                ss_tree = ET.fromstring(ss_xml)
                ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
                for si in ss_tree.iter('{%s}si' % ns):
                    texts = [t.text or '' for t in si.iter('{%s}t' % ns)]
                    shared_strings.append(''.join(texts))
            # Read first sheet
            sheet_xml = zf.read('xl/worksheets/sheet1.xml')
            sheet_tree = ET.fromstring(sheet_xml)
            ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
            rows = []
            for row in list(sheet_tree.iter('{%s}row' % ns))[:200]:
                cells = []
                for cell in row.iter('{%s}c' % ns):
                    val_el = cell.find('{%s}v' % ns)
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

    def _extract_image_ocr(self):
        """Extract text from image via local OCR, then Document Intelligence."""
        import base64
        try:
            import pytesseract
            from PIL import Image
            import io
            raw = base64.b64decode(self.attachment_id.datas)
            img = Image.open(io.BytesIO(raw))
            text = pytesseract.image_to_string(img, lang='eng')
            if text and text.strip():
                return text.strip(), 'image_ocr_local'
        except Exception as e:
            _logger.debug('Local image OCR failed: %s', e)
        return self._extract_via_doc_intelligence('prebuilt-read')

    def _extract_via_doc_intelligence(self, model_id):
        """Use Azure Document Intelligence for extraction.

        Returns (text, method) tuple.
        """
        self.ensure_one()
        try:
            svc = self.env['ipai.doc.intelligence.service']
            result = svc.analyze_document(
                self.attachment_id.id, model_id=model_id,
            )
            if result.get('status') == 'success':
                analyze_result = result.get('result', {})
                content = analyze_result.get('content', '')
                return content, 'doc_intelligence'
        except Exception as e:
            _logger.warning('Document Intelligence extraction failed: %s', e)
        return '', 'ocr_unavailable'

    @staticmethod
    def _estimate_tokens(text):
        """Rough token estimate: ~4 chars per token for English."""
        if not text:
            return 0
        return len(text) // 4
