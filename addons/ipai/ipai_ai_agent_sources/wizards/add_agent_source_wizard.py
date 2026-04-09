# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AddAgentSourceWizard(models.TransientModel):
    _name = "ipai.ai.agent.source.wizard"
    _description = "Add Agent Source"

    agent_id = fields.Many2one(
        "ipai.ai.agent",
        required=True,
        default=lambda self: self.env.context.get("default_agent_id"),
    )
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
        default="pdf",
    )

    # Type-specific fields
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Files",
        help="Upload one or more files.",
    )
    url = fields.Char(string="Web URL")
    knowledge_ref = fields.Char(string="Knowledge Reference")
    auto_submit = fields.Boolean(
        default=True,
        help="Automatically submit for indexing after creation.",
    )

    @api.constrains("source_type", "attachment_ids", "url", "knowledge_ref")
    def _check_source_content(self):
        for wiz in self:
            if wiz.source_type in ("pdf", "docx", "xlsx", "pptx", "image", "document"):
                if not wiz.attachment_ids:
                    raise ValidationError(
                        "Please upload at least one file for source type '%s'."
                        % wiz.source_type
                    )
            elif wiz.source_type == "weblink":
                if not wiz.url:
                    raise ValidationError("Please provide a URL for weblink source.")
            elif wiz.source_type == "knowledge":
                if not wiz.knowledge_ref:
                    raise ValidationError(
                        "Please provide a knowledge reference."
                    )

    def action_add_sources(self):
        """Create source records and optionally submit for indexing."""
        self.ensure_one()
        Source = self.env["ipai.ai.agent.source"]
        created = Source

        if self.source_type in ("pdf", "docx", "xlsx", "pptx", "image", "document"):
            for att in self.attachment_ids:
                created |= Source.create({
                    "name": att.name,
                    "agent_id": self.agent_id.id,
                    "source_type": self.source_type,
                    "attachment_id": att.id,
                })
        elif self.source_type == "weblink":
            created |= Source.create({
                "name": self.url,
                "agent_id": self.agent_id.id,
                "source_type": "weblink",
                "url": self.url,
            })
        elif self.source_type == "knowledge":
            created |= Source.create({
                "name": "Knowledge: %s" % self.knowledge_ref,
                "agent_id": self.agent_id.id,
                "source_type": "knowledge",
                "knowledge_ref": self.knowledge_ref,
            })

        if self.auto_submit and created:
            created.action_submit_for_indexing()

        return {"type": "ir.actions.act_window_close"}
