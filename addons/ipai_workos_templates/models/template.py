# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models


class IpaiWorkosTemplate(models.Model):
    """Template - Reusable page or database structure."""

    _name = "ipai.workos.template"
    _description = "Work OS Template"
    _order = "category, sequence, name"

    name = fields.Char(string="Template Name", required=True)
    description = fields.Text(string="Description")
    icon = fields.Char(string="Icon", default="file-o")
    category = fields.Selection(
        [
            ("page", "Page Template"),
            ("database", "Database Template"),
        ],
        string="Category",
        required=True,
        default="page",
    )
    sequence = fields.Integer(string="Sequence", default=10)

    # Template content
    blocks_json = fields.Text(
        string="Blocks (JSON)",
        default="[]",
        help="For page templates: array of block definitions",
    )
    properties_json = fields.Text(
        string="Properties (JSON)",
        default="[]",
        help="For database templates: array of property definitions",
    )
    views_json = fields.Text(
        string="Views (JSON)",
        default="[]",
        help="For database templates: default views to create",
    )

    # Tags for discovery
    tag_ids = fields.Many2many(
        "ipai.workos.template.tag",
        string="Tags",
    )

    # Status
    is_system = fields.Boolean(
        string="System Template",
        default=False,
        help="System templates cannot be deleted",
    )
    is_published = fields.Boolean(
        string="Published",
        default=True,
    )

    def get_blocks(self):
        """Get parsed blocks array."""
        try:
            return json.loads(self.blocks_json or "[]")
        except json.JSONDecodeError:
            return []

    def get_properties(self):
        """Get parsed properties array."""
        try:
            return json.loads(self.properties_json or "[]")
        except json.JSONDecodeError:
            return []

    def apply_to_page(self, page):
        """Apply template blocks to a page."""
        page.template_id = self.id
        Block = self.env["ipai.workos.block"]
        blocks = self.get_blocks()
        for idx, block_def in enumerate(blocks):
            Block.create({
                "page_id": page.id,
                "block_type": block_def.get("type", "paragraph"),
                "content_json": json.dumps(block_def.get("content", {})),
                "sequence": (idx + 1) * 10,
            })
        return page

    def apply_to_database(self, database):
        """Apply template properties and views to a database."""
        Property = self.env["ipai.workos.property"]
        View = self.env["ipai.workos.view"]

        # Create properties
        properties = self.get_properties()
        for idx, prop_def in enumerate(properties):
            Property.create({
                "database_id": database.id,
                "name": prop_def.get("name", f"Property {idx + 1}"),
                "property_type": prop_def.get("type", "text"),
                "sequence": (idx + 1) * 10,
                "is_title": prop_def.get("is_title", False),
                "options_json": json.dumps(prop_def.get("options", [])),
            })

        # Create default views
        views = json.loads(self.views_json or "[]")
        for view_def in views:
            View.create({
                "database_id": database.id,
                "name": view_def.get("name", "Default"),
                "view_type": view_def.get("type", "table"),
                "is_default": view_def.get("is_default", False),
            })

        return database


class IpaiWorkosTemplateTag(models.Model):
    """Template Tag for categorization."""

    _name = "ipai.workos.template.tag"
    _description = "Work OS Template Tag"

    name = fields.Char(string="Tag", required=True)
    color = fields.Integer(string="Color Index", default=0)
