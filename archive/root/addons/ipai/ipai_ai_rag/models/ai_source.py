# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import base64
import logging

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiAiSource(models.Model):
    """Knowledge source for RAG retrieval."""

    _name = "ipai.ai.source"
    _description = "IPAI AI Source"
    _order = "name"

    name = fields.Char(
        string="Name",
        required=True,
        index=True,
    )
    agent_id = fields.Many2one(
        comodel_name="ipai.ai.agent",
        string="Agent",
        required=True,
        ondelete="cascade",
        index=True,
    )
    source_type = fields.Selection(
        selection=[
            ("file", "File"),
            ("url", "URL"),
            ("kb", "Knowledge Base"),
            ("model_field", "Model Field"),
        ],
        string="Type",
        required=True,
        default="file",
    )
    locator = fields.Text(
        string="Locator",
        help="File path, URL, KB reference, or model.field reference.",
    )
    file_content = fields.Binary(
        string="File",
        attachment=True,
    )
    file_name = fields.Char(
        string="File Name",
    )
    metadata = fields.Text(
        string="Metadata (JSON)",
        help="Additional metadata as JSON.",
    )
    ingest_status = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("done", "Done"),
            ("error", "Error"),
        ],
        string="Ingest Status",
        default="pending",
        required=True,
    )
    ingest_error = fields.Text(
        string="Ingest Error",
    )
    chunk_ids = fields.One2many(
        comodel_name="ipai.ai.chunk",
        inverse_name="source_id",
        string="Chunks",
    )
    chunk_count = fields.Integer(
        string="Chunk Count",
        compute="_compute_chunk_count",
        store=True,
    )
    company_id = fields.Many2one(
        related="agent_id.company_id",
        string="Company",
        store=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    @api.depends("chunk_ids")
    def _compute_chunk_count(self):
        for source in self:
            source.chunk_count = len(source.chunk_ids)

    def action_ingest(self):
        """Trigger ingestion for this source."""
        self.ensure_one()
        self.write({"ingest_status": "processing", "ingest_error": False})

        try:
            # Get content based on source type
            content = self._get_content()
            if not content:
                raise UserError("No content to ingest.")

            # Chunk the content
            chunking_service = self.env["ipai.ai.chunking.service"]
            chunks_data = chunking_service.chunk_text(content)

            # Delete existing chunks
            self.chunk_ids.unlink()

            # Create new chunks
            for idx, chunk_data in enumerate(chunks_data):
                self.env["ipai.ai.chunk"].create({
                    "source_id": self.id,
                    "index": idx,
                    "content": chunk_data["content"],
                    "content_hash": chunk_data["hash"],
                    "token_count": chunk_data["token_count"],
                })

            # Generate embeddings
            embedding_service = self.env["ipai.ai.embedding.service"]
            embedding_service.generate_embeddings_for_source(self)

            self.write({"ingest_status": "done"})
            _logger.info(f"Ingested source {self.id}: {len(chunks_data)} chunks")

        except Exception as e:
            _logger.exception(f"Error ingesting source {self.id}")
            self.write({
                "ingest_status": "error",
                "ingest_error": str(e),
            })
            raise

    def _get_content(self):
        """Get content from the source based on its type."""
        self.ensure_one()

        if self.source_type == "file":
            if not self.file_content:
                raise UserError("No file uploaded.")
            content = base64.b64decode(self.file_content).decode("utf-8", errors="ignore")
            return content

        elif self.source_type == "url":
            if not self.locator:
                raise UserError("No URL specified.")
            try:
                response = requests.get(self.locator, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                raise UserError(f"Failed to fetch URL: {e}")

        elif self.source_type == "kb":
            # Knowledge base reference - to be implemented based on KB structure
            raise UserError("Knowledge Base source type not yet implemented.")

        elif self.source_type == "model_field":
            if not self.locator:
                raise UserError("No model.field reference specified.")
            # Format: model_name:field_name:domain
            parts = self.locator.split(":", 2)
            if len(parts) < 2:
                raise UserError("Invalid model_field format. Use: model_name:field_name[:domain]")
            model_name, field_name = parts[0], parts[1]
            domain = eval(parts[2]) if len(parts) > 2 else []

            try:
                records = self.env[model_name].search(domain)
                contents = []
                for record in records:
                    value = getattr(record, field_name, "")
                    if value:
                        contents.append(str(value))
                return "\n\n".join(contents)
            except Exception as e:
                raise UserError(f"Failed to read model field: {e}")

        return None

    def action_reset(self):
        """Reset source to pending state."""
        self.ensure_one()
        self.chunk_ids.unlink()
        self.write({
            "ingest_status": "pending",
            "ingest_error": False,
        })
