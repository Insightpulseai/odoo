# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

"""Copilot attachment reference model.

Wraps ir.attachment with ingestion metadata and extracted text
for copilot prompt injection. Supports plain text, JSON, and CSV
extraction natively; falls back to Azure Document Intelligence for
PDF/Office formats.
"""

import base64
import hashlib
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

DIRECT_MIME_TYPES = {
    "text/plain",
    "text/csv",
    "text/markdown",
    "application/json",
    "application/xml",
    "text/xml",
    "text/html",
}


class CopilotAttachmentRef(models.Model):
    _name = "ipai.copilot.attachment.ref"
    _description = "Copilot Attachment Reference"
    _order = "create_date asc, id asc"

    # -------------------------------------------------------------------------
    # Relations
    # -------------------------------------------------------------------------
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Attachment",
        required=True,
        ondelete="cascade",
        index=True,
    )
    conversation_id = fields.Many2one(
        "ipai.copilot.conversation",
        string="Conversation",
        ondelete="cascade",
        index=True,
    )
    message_id = fields.Many2one(
        "ipai.copilot.message",
        string="Message",
        ondelete="set null",
        index=True,
    )

    # -------------------------------------------------------------------------
    # File metadata
    # -------------------------------------------------------------------------
    filename = fields.Char(
        string="Filename",
        required=True,
    )
    mime_type = fields.Char(
        string="MIME Type",
        required=True,
    )
    file_size = fields.Integer(
        string="File Size (bytes)",
        readonly=True,
    )
    content_sha256 = fields.Char(
        string="SHA256",
        readonly=True,
        size=64,
    )
    origin = fields.Selection(
        [
            ("upload", "User Upload"),
            ("odoo", "Odoo Record"),
            ("url", "External URL"),
        ],
        default="upload",
        required=True,
    )

    # -------------------------------------------------------------------------
    # Ingestion state machine
    # -------------------------------------------------------------------------
    ingestion_state = fields.Selection(
        [
            ("pending", "Pending"),
            ("extracting", "Extracting"),
            ("extracted", "Extracted"),
            ("done", "Done"),
            ("skip", "Skipped"),
            ("error", "Error"),
        ],
        default="pending",
        required=True,
        index=True,
    )
    extraction_method = fields.Selection(
        [
            ("direct", "Direct (text/JSON/CSV)"),
            ("doc_intelligence", "Azure Document Intelligence"),
            ("none", "None"),
        ],
        string="Extraction Method",
        readonly=True,
    )
    extracted_text = fields.Text(
        string="Extracted Text",
        readonly=True,
    )
    token_estimate = fields.Integer(
        string="Token Estimate",
        readonly=True,
        help="Rough token count: len(extracted_text) // 4",
    )
    extraction_error = fields.Char(
        string="Extraction Error",
        readonly=True,
    )

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._compute_file_metadata()
        return records

    def _compute_file_metadata(self):
        """Compute SHA256 and file size from the linked ir.attachment."""
        self.ensure_one()
        if not self.attachment_id:
            return
        raw_datas = self.attachment_id.datas
        if not raw_datas:
            self.file_size = 0
            self.content_sha256 = ""
            return
        try:
            binary_content = base64.b64decode(raw_datas)
            self.file_size = len(binary_content)
            self.content_sha256 = hashlib.sha256(binary_content).hexdigest()
        except Exception as exc:
            _logger.warning("Failed to compute metadata for attachment ref %s: %s", self.id, exc)

    # -------------------------------------------------------------------------
    # Extraction
    # -------------------------------------------------------------------------
    def run_extraction(self):
        """Run text extraction for refs in pending or error state."""
        for rec in self:
            if rec.ingestion_state not in ("pending", "error"):
                continue
            rec._do_extract()

    def _do_extract(self):
        """Internal extraction dispatcher."""
        self.ensure_one()
        attachment = self.attachment_id
        raw_datas = attachment.datas
        if not raw_datas:
            self.ingestion_state = "skip"
            self.extraction_method = "none"
            return

        try:
            binary_content = base64.b64decode(raw_datas)
        except Exception as exc:
            self.ingestion_state = "error"
            self.extraction_error = str(exc)
            return

        if not binary_content:
            self.ingestion_state = "skip"
            self.extraction_method = "none"
            return

        mime = (self.mime_type or "").lower()
        if mime in DIRECT_MIME_TYPES or mime.startswith("text/"):
            self._extract_direct(binary_content)
        else:
            # Non-text formats: stay pending for async extraction (e.g. DI)
            self.extraction_method = "none"

    def _extract_direct(self, binary_content):
        """Extract text directly from text-based files."""
        self.ensure_one()
        try:
            text = binary_content.decode("utf-8", errors="replace")
        except Exception as exc:
            self.ingestion_state = "error"
            self.extraction_error = str(exc)
            return

        self.extracted_text = text
        self.token_estimate = len(text) // 4
        self.extraction_method = "direct"
        self.ingestion_state = "done"
