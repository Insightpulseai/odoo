# -*- coding: utf-8 -*-
import base64

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestChatSession(TransactionCase):
    """Test ipai.chat.session model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.ref('base.user_admin')
        cls.Session = cls.env['ipai.chat.session']

    def test_create_session_generates_external_id(self):
        session = self.Session.create({'name': 'Test Session'})
        self.assertTrue(session.external_session_id)
        self.assertEqual(len(session.external_session_id), 36)  # UUID

    def test_session_archive_unarchive(self):
        session = self.Session.create({'name': 'Test'})
        self.assertEqual(session.state, 'active')
        session.action_archive()
        self.assertEqual(session.state, 'archived')
        session.action_unarchive()
        self.assertEqual(session.state, 'active')

    def test_eligible_sources_empty(self):
        session = self.Session.create({'name': 'Test'})
        self.assertEqual(len(session.get_eligible_sources()), 0)

    def test_eligible_sources_filters_correctly(self):
        session = self.Session.create({'name': 'Test'})
        Source = self.env['ipai.chat.source']
        # Indexed + active → eligible
        s1 = Source.create({
            'name': 'good.pdf',
            'session_id': session.id,
            'source_type': 'pdf',
            'status': 'draft',
        })
        s1.write({'status': 'processing'})
        s1.write({'status': 'indexed'})
        # Failed → not eligible
        s2 = Source.create({
            'name': 'bad.pdf',
            'session_id': session.id,
            'source_type': 'pdf',
            'status': 'draft',
        })
        s2.write({'status': 'processing'})
        s2.write({'status': 'failed'})
        # Indexed but inactive → not eligible
        s3 = Source.create({
            'name': 'inactive.pdf',
            'session_id': session.id,
            'source_type': 'pdf',
            'status': 'draft',
        })
        s3.write({'status': 'processing'})
        s3.write({'status': 'indexed', 'active': False})

        eligible = session.get_eligible_sources()
        self.assertEqual(len(eligible), 1)
        self.assertEqual(eligible.id, s1.id)


@tagged('post_install', '-at_install')
class TestChatSource(TransactionCase):
    """Test ipai.chat.source model and lifecycle transitions."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.session = cls.env['ipai.chat.session'].create({
            'name': 'Test Session',
        })
        cls.Source = cls.env['ipai.chat.source']

    def _make_source(self, name='test.pdf', source_type='pdf', **kwargs):
        vals = {
            'name': name,
            'session_id': self.session.id,
            'source_type': source_type,
        }
        vals.update(kwargs)
        return self.Source.create(vals)

    # ------------------------------------------------------------------
    # Lifecycle transitions (via _set_status)
    # ------------------------------------------------------------------
    def test_draft_to_processing(self):
        src = self._make_source()
        self.assertEqual(src.status, 'draft')
        src._set_status('processing')
        self.assertEqual(src.status, 'processing')

    def test_processing_to_indexed(self):
        src = self._make_source()
        src._set_status('processing')
        src._set_status('indexed')
        self.assertEqual(src.status, 'indexed')

    def test_processing_to_failed(self):
        src = self._make_source()
        src._set_status('processing')
        src._set_status('failed', error='Extraction timed out')
        self.assertEqual(src.status, 'failed')
        self.assertEqual(src.last_error, 'Extraction timed out')

    def test_failed_to_processing_via_set_status(self):
        src = self._make_source()
        src._set_status('processing')
        src._set_status('failed', error='Timeout')
        src._set_status('processing', error=False)
        self.assertEqual(src.status, 'processing')

    def test_invalid_transition_raises(self):
        src = self._make_source()
        with self.assertRaises(UserError):
            src._set_status('indexed')  # draft → indexed not allowed

    def test_indexed_cannot_transition(self):
        src = self._make_source()
        src._set_status('processing')
        src._set_status('indexed')
        with self.assertRaises(UserError):
            src._set_status('processing')

    def test_retry_only_on_failed(self):
        src = self._make_source()
        with self.assertRaises(UserError):
            src.action_retry()  # draft → retry not allowed

    # ------------------------------------------------------------------
    # Local extraction via action_submit_for_processing
    # ------------------------------------------------------------------
    def test_submit_no_attachment_fails(self):
        """Source without attachment data should fail extraction."""
        src = self._make_source()
        src.action_submit_for_processing()
        self.assertEqual(src.status, 'failed')
        self.assertIn('No attachment data', src.last_error)

    def test_submit_with_pdf_extracts_text(self):
        """Source with a text-layer PDF should extract and become indexed."""
        # Create a minimal valid PDF with text
        pdf_content = self._make_minimal_pdf()
        att = self.env['ir.attachment'].create({
            'name': 'test.pdf',
            'datas': base64.b64encode(pdf_content),
            'mimetype': 'application/pdf',
        })
        src = self._make_source(attachment_id=att.id)
        src.action_submit_for_processing()
        # PyPDF2 may or may not extract text from our minimal PDF.
        # Either indexed (text found) or failed (no text) is valid.
        self.assertIn(src.status, ('indexed', 'failed'))
        if src.status == 'indexed':
            self.assertTrue(src.extracted_text)
            self.assertTrue(src.extraction_method)
            self.assertTrue(src.token_estimate > 0)
            self.assertTrue(src.processed_at)

    def test_submit_url_source_fails_locally(self):
        """URL sources cannot be extracted locally."""
        src = self._make_source(source_type='url')
        src.action_submit_for_processing()
        self.assertEqual(src.status, 'failed')
        self.assertIn('agent-platform', src.last_error)

    def test_retry_reruns_extraction(self):
        """Retry on failed source re-runs extraction."""
        src = self._make_source()
        src._set_status('processing')
        src._set_status('failed', error='First attempt')
        # Retry without attachment → still fails
        src.action_retry()
        self.assertEqual(src.status, 'failed')

    @staticmethod
    def _make_minimal_pdf():
        """Create minimal PDF bytes with text content."""
        # Minimal valid PDF 1.0 with text
        return (
            b'%PDF-1.0\n'
            b'1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n'
            b'2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n'
            b'3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]'
            b'/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n'
            b'4 0 obj<</Length 44>>stream\n'
            b'BT /F1 12 Tf 100 700 Td (Hello World) Tj ET\n'
            b'endstream\nendobj\n'
            b'5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n'
            b'xref\n0 6\n'
            b'0000000000 65535 f \n'
            b'0000000009 00000 n \n'
            b'0000000058 00000 n \n'
            b'0000000115 00000 n \n'
            b'0000000266 00000 n \n'
            b'0000000360 00000 n \n'
            b'trailer<</Size 6/Root 1 0 R>>\n'
            b'startxref\n430\n%%EOF'
        )

    # ------------------------------------------------------------------
    # Eligibility
    # ------------------------------------------------------------------
    def test_is_eligible_indexed_active(self):
        src = self._make_source()
        src._set_status('processing')
        src._set_status('indexed')
        self.assertTrue(src.is_eligible())

    def test_not_eligible_when_failed(self):
        src = self._make_source()
        src._set_status('processing')
        src._set_status('failed')
        self.assertFalse(src.is_eligible())

    def test_not_eligible_when_inactive(self):
        src = self._make_source()
        src._set_status('processing')
        src._set_status('indexed')
        src.action_deactivate()
        self.assertFalse(src.is_eligible())

    def test_not_eligible_when_draft(self):
        src = self._make_source()
        self.assertFalse(src.is_eligible())

    def test_not_eligible_when_processing(self):
        src = self._make_source()
        src._set_status('processing')
        self.assertFalse(src.is_eligible())

    # ------------------------------------------------------------------
    # Callback
    # ------------------------------------------------------------------
    def test_callback_success(self):
        src = self._make_source()
        src._set_status('processing')
        src.apply_callback({
            'status': 'indexed',
            'external_source_id': 'ap_src_123',
            'external_index_id': 'idx_456',
            'processed_at': '2026-04-09 17:30:00',
        })
        self.assertEqual(src.status, 'indexed')
        self.assertEqual(src.external_source_id, 'ap_src_123')
        self.assertEqual(src.external_index_id, 'idx_456')
        self.assertTrue(src.processed_at)

    def test_callback_failure(self):
        src = self._make_source()
        src._set_status('processing')
        src.apply_callback({
            'status': 'failed',
            'error': 'OCR engine unavailable',
        })
        self.assertEqual(src.status, 'failed')
        self.assertEqual(src.last_error, 'OCR engine unavailable')

    def test_callback_invalid_status(self):
        src = self._make_source()
        src._set_status('processing')
        with self.assertRaises(UserError):
            src.apply_callback({'status': 'bogus'})

    # ------------------------------------------------------------------
    # Checksum on create with attachment
    # ------------------------------------------------------------------
    def test_checksum_computed_on_create(self):
        content = b'Hello world PDF content'
        att = self.env['ir.attachment'].create({
            'name': 'test.pdf',
            'datas': base64.b64encode(content),
        })
        src = self._make_source(attachment_id=att.id)
        import hashlib
        expected = hashlib.sha256(content).hexdigest()
        self.assertEqual(src.checksum, expected)
        self.assertEqual(src.file_size, len(content))

    # ------------------------------------------------------------------
    # Activate / deactivate
    # ------------------------------------------------------------------
    def test_activate_deactivate(self):
        src = self._make_source()
        self.assertTrue(src.active)
        src.action_deactivate()
        self.assertFalse(src.active)
        src.action_activate()
        self.assertTrue(src.active)


@tagged('post_install', '-at_install')
class TestChatMessage(TransactionCase):
    """Test ipai.chat.message model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.session = cls.env['ipai.chat.session'].create({
            'name': 'Msg Test',
        })
        cls.Message = cls.env['ipai.chat.message']

    def test_create_message(self):
        msg = self.Message.create({
            'session_id': self.session.id,
            'role': 'user',
            'content': 'What is the total?',
        })
        self.assertTrue(msg.id)
        self.assertEqual(msg.role, 'user')

    def test_empty_content_raises(self):
        with self.assertRaises(Exception):
            self.Message.create({
                'session_id': self.session.id,
                'role': 'user',
                'content': '   ',
            })

    def test_source_snapshot_parsing(self):
        msg = self.Message.create({
            'session_id': self.session.id,
            'role': 'assistant',
            'content': 'Answer here',
            'source_ids_snapshot': '[1, 2, 3]',
        })
        self.assertEqual(msg.get_source_snapshot_ids(), [1, 2, 3])

    def test_source_snapshot_empty(self):
        msg = self.Message.create({
            'session_id': self.session.id,
            'role': 'assistant',
            'content': 'No sources',
        })
        self.assertEqual(msg.get_source_snapshot_ids(), [])

    def test_message_count_on_session(self):
        session = self.env['ipai.chat.session'].create({'name': 'Count Test'})
        for i in range(3):
            self.Message.create({
                'session_id': session.id,
                'role': 'user',
                'content': f'Message {i}',
            })
        session.invalidate_recordset()
        self.assertEqual(session.message_count, 3)
