# -*- coding: utf-8 -*-

import hashlib
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiAiAgentSource(models.Model):
    _name = "ipai.ai.agent.source"
    _description = "AI Agent Source"
    _inherit = ["mail.thread"]
    _order = "status, name"
    _rec_name = "name"

    name = fields.Char(required=True, tracking=True)
    agent_id = fields.Many2one(
        "ipai.ai.agent",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    active = fields.Boolean(default=True, tracking=True)
    company_id = fields.Many2one(
        related="agent_id.company_id", store=True,
    )

    # Source type
    source_type = fields.Selection(
        [
            ("pdf", "PDF"),
            ("weblink", "Web Link"),
            ("document", "Odoo Document"),
            ("knowledge", "Knowledge Article"),
            ("docx", "DOCX"),
            ("xlsx", "XLSX"),
            ("pptx", "PPTX"),
            ("image", "Image"),
        ],
        required=True,
        tracking=True,
    )

    # Source content pointers (exactly one populated per source_type)
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Uploaded File",
        help="For pdf/docx/xlsx/pptx/image sources.",
    )
    url = fields.Char(
        string="Web URL",
        help="For weblink sources.",
    )
    knowledge_ref = fields.Char(
        string="Knowledge Reference",
        help="Knowledge article reference or ID.",
    )

    # Lifecycle
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("processing", "Processing"),
            ("indexed", "Indexed"),
            ("failed", "Failed"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # External identifiers (populated by agent-platform callback)
    external_source_id = fields.Char(
        string="External Source ID",
        help="Document ID in agent-platform / Azure AI Search.",
    )
    external_index_id = fields.Char(
        string="External Index ID",
        help="Index identifier in Azure AI Search.",
    )

    # Diagnostics
    last_error = fields.Text()
    processed_at = fields.Datetime()
    checksum = fields.Char(
        string="Content Checksum",
        help="SHA-256 of the source content at last indexing.",
    )

    # Run history
    run_ids = fields.One2many(
        "ipai.ai.agent.source.run", "source_id", string="Indexing Runs",
    )
    run_count = fields.Integer(compute="_compute_run_count")

    # Metadata
    file_size = fields.Integer(
        related="attachment_id.file_size", string="File Size",
    )
    mimetype = fields.Char(
        related="attachment_id.mimetype", string="MIME Type",
    )

    def _compute_run_count(self):
        for source in self:
            source.run_count = len(source.run_ids)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_submit_for_indexing(self):
        """Submit source(s) to agent-platform for extraction + indexing."""
        bridge = self.env["ipai.ai.agent.source.bridge"]
        for source in self:
            if source.status == "processing":
                continue
            source._compute_checksum()
            source.write({"status": "processing", "last_error": False})
            source.message_post(body="Submitted for indexing.")
            bridge.submit_source(source)

    def action_reindex(self):
        """Force re-indexing of already indexed sources."""
        self.action_submit_for_indexing()

    def action_deactivate(self):
        self.write({"active": False})

    def action_activate(self):
        indexed = self.filtered(lambda s: s.status == "indexed")
        if not indexed:
            raise UserError("Only indexed sources can be activated.")
        indexed.write({"active": True})

    # ------------------------------------------------------------------
    # Callbacks (called by agent-platform via controller or service)
    # ------------------------------------------------------------------

    def callback_indexed(self, external_source_id, external_index_id):
        """Called when agent-platform successfully indexes this source."""
        self.ensure_one()
        self.write({
            "status": "indexed",
            "external_source_id": external_source_id,
            "external_index_id": external_index_id,
            "processed_at": fields.Datetime.now(),
            "last_error": False,
        })
        self.env["ipai.ai.agent.source.run"].create({
            "source_id": self.id,
            "status": "success",
            "external_source_id": external_source_id,
        })
        self.message_post(body="Source indexed successfully.")

    def callback_failed(self, error_message):
        """Called when agent-platform fails to index this source."""
        self.ensure_one()
        self.write({
            "status": "failed",
            "last_error": error_message,
            "processed_at": fields.Datetime.now(),
        })
        self.env["ipai.ai.agent.source.run"].create({
            "source_id": self.id,
            "status": "failed",
            "error_message": error_message,
        })
        self.message_post(
            body="Indexing failed: %s" % error_message,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _compute_checksum(self):
        """Compute SHA-256 checksum of source content."""
        for source in self:
            if source.attachment_id and source.attachment_id.datas:
                import base64
                raw = base64.b64decode(source.attachment_id.datas)
                source.checksum = hashlib.sha256(raw).hexdigest()
            elif source.url:
                source.checksum = hashlib.sha256(
                    source.url.encode()
                ).hexdigest()
            elif source.knowledge_ref:
                source.checksum = hashlib.sha256(
                    source.knowledge_ref.encode()
                ).hexdigest()

    def _get_active_indexed_sources(self, agent_id):
        """Return active indexed sources for a given agent."""
        return self.search([
            ("agent_id", "=", agent_id),
            ("status", "=", "indexed"),
            ("active", "=", True),
        ])


class IpaiAiAgentSourceRun(models.Model):
    _name = "ipai.ai.agent.source.run"
    _description = "Agent Source Indexing Run"
    _order = "create_date desc"

    source_id = fields.Many2one(
        "ipai.ai.agent.source",
        required=True,
        ondelete="cascade",
    )
    status = fields.Selection(
        [("success", "Success"), ("failed", "Failed")],
        required=True,
    )
    external_source_id = fields.Char()
    error_message = fields.Text()
    duration_ms = fields.Integer()
