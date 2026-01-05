# -*- coding: utf-8 -*-
"""IPAI Agent Knowledge Source model - documents, URLs, models for context."""

from odoo import api, fields, models


class IpaiAgentKnowledgeSource(models.Model):
    """Knowledge source for agent context enrichment."""

    _name = "ipai.agent.knowledge_source"
    _description = "IPAI Agent Knowledge Source"
    _order = "name"

    name = fields.Char(required=True, index=True)
    key = fields.Char(
        required=True, index=True, help="Stable identifier, e.g. 'odoo18.ce.dev'"
    )

    kind = fields.Selection(
        [
            ("attachment", "Attachment"),
            ("url", "URL"),
            ("model", "Odoo Model"),
            ("text", "Inline Text"),
        ],
        default="text",
        required=True,
    )

    # Source content based on kind
    url = fields.Char(help="URL for kind=url")
    model_name = fields.Char(help="Model name for kind=model")
    attachment_id = fields.Many2one(
        "ir.attachment", string="Attachment", help="File attachment for kind=attachment"
    )
    content_text = fields.Text(help="Inline content for kind=text")

    tags = fields.Char(help="Comma-separated tags for filtering")
    is_active = fields.Boolean(default=True)

    _sql_constraints = [
        ("knowledge_key_unique", "unique(key)", "Knowledge key must be unique."),
    ]

    def get_tags_list(self):
        """Return list of tags from comma-separated field."""
        self.ensure_one()
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    def get_content(self):
        """
        Retrieve content based on kind.

        Returns:
            str: Content text (or description for complex sources)
        """
        self.ensure_one()

        if self.kind == "text":
            return self.content_text or ""

        elif self.kind == "url":
            return f"[URL Source: {self.url}]"

        elif self.kind == "model":
            return f"[Odoo Model: {self.model_name}]"

        elif self.kind == "attachment":
            if self.attachment_id:
                return f"[Attachment: {self.attachment_id.name}]"
            return "[No attachment]"

        return ""

    def to_context_dict(self):
        """Return knowledge source as context dictionary for agents."""
        self.ensure_one()
        return {
            "key": self.key,
            "name": self.name,
            "kind": self.kind,
            "tags": self.get_tags_list(),
            "content": self.get_content(),
        }
