# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiWorkosPage(models.Model):
    """Page - Content container with blocks, supporting nested pages."""

    _name = "ipai.workos.page"
    _description = "Work OS Page"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(string="Title", required=True, tracking=True)
    icon = fields.Char(string="Icon", default="file-text")
    cover_image = fields.Binary(string="Cover Image", attachment=True)
    sequence = fields.Integer(string="Sequence", default=10)

    # Hierarchy
    parent_id = fields.Many2one(
        "ipai.workos.page",
        string="Parent Page",
        ondelete="cascade",
        index=True,
    )
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many(
        "ipai.workos.page",
        "parent_id",
        string="Sub-pages",
    )
    child_count = fields.Integer(
        string="Sub-pages",
        compute="_compute_child_count",
    )

    # Space (root pages belong to a space)
    space_id = fields.Many2one(
        "ipai.workos.space",
        string="Space",
        ondelete="cascade",
        compute="_compute_space_id",
        store=True,
        recursive=True,
    )

    # Workspace (computed from space)
    workspace_id = fields.Many2one(
        "ipai.workos.workspace",
        string="Workspace",
        related="space_id.workspace_id",
        store=True,
    )

    # Content (blocks are stored in ipai_workos_blocks module)
    content_preview = fields.Text(
        string="Content Preview",
        compute="_compute_content_preview",
    )

    # Template reference
    template_id = fields.Many2one(
        "ipai.workos.template",
        string="Created from Template",
    )

    # Status
    active = fields.Boolean(default=True)
    is_archived = fields.Boolean(string="Archived", default=False)

    # Timestamps
    last_edited_by = fields.Many2one(
        "res.users",
        string="Last Edited By",
        compute="_compute_last_edited",
        store=True,
    )

    @api.depends("child_ids")
    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.child_ids)

    @api.depends("parent_id", "parent_id.space_id")
    def _compute_space_id(self):
        for record in self:
            if record.parent_id:
                record.space_id = record.parent_id.space_id
            # If no parent, space_id should be set directly

    def _compute_content_preview(self):
        """Compute preview from blocks (if blocks module is installed)."""
        for record in self:
            # This will be populated by ipai_workos_blocks
            record.content_preview = ""

    @api.depends("write_uid")
    def _compute_last_edited(self):
        for record in self:
            record.last_edited_by = record.write_uid

    def action_archive(self):
        """Archive the page."""
        self.write({"is_archived": True, "active": False})

    def action_restore(self):
        """Restore archived page."""
        self.write({"is_archived": False, "active": True})

    def action_view_subpages(self):
        """Open sub-pages of this page."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Sub-pages of {self.name}",
            "res_model": "ipai.workos.page",
            "view_mode": "tree,form",
            "domain": [("parent_id", "=", self.id)],
            "context": {
                "default_parent_id": self.id,
                "default_space_id": self.space_id.id,
            },
        }

    @api.model
    def get_page_tree(self, space_id):
        """Get hierarchical page tree for sidebar navigation."""
        pages = self.search(
            [
                ("space_id", "=", space_id),
                ("parent_id", "=", False),
            ]
        )
        return self._build_tree(pages)

    def _build_tree(self, pages):
        """Recursively build page tree structure."""
        result = []
        for page in pages:
            node = {
                "id": page.id,
                "name": page.name,
                "icon": page.icon,
                "children": self._build_tree(page.child_ids),
            }
            result.append(node)
        return result
