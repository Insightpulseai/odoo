# -*- coding: utf-8 -*-
"""
IPAI Knowledge Document Model.

This module provides Notion-style document management for Odoo CE:
- Hierarchical document structure (parent/child pages)
- Document lifecycle (draft → in_review → published → archived)
- Block-based content storage (JSON) with HTML rendering
- Template support for document cloning
- Collaborative editing with owner and collaborator roles

Models:
    IpaiDoc: Main document model with versioning and collaboration features
"""
from odoo import _, api, fields, models


class IpaiDoc(models.Model):
    """
    IPAI Knowledge Document Model.

    Implements a Notion-style document system with hierarchical pages,
    block-based content, and collaborative editing features.

    Workflow:
        draft → in_review → published → archived

    Features:
        - Nested page hierarchy (parent_id/child_ids)
        - JSON block storage for rich content
        - Template cloning support
        - Owner and collaborator permissions

    Attributes:
        _name: ipai.doc
        _description: IPAI Knowledge Document
        _inherit: mail.thread, mail.activity.mixin
    """

    _name = "ipai.doc"
    _description = "IPAI Knowledge Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    name = fields.Char(
        string="Title",
        required=True,
        tracking=True,
    )

    sequence = fields.Integer(default=10)

    doc_type = fields.Selection(
        [
            ("page", "Page"),
            ("sop", "SOP / Playbook"),
            ("meeting_notes", "Meeting Notes"),
            ("spec", "Spec / PRD"),
            ("other", "Other"),
        ],
        string="Type",
        default="page",
        tracking=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_review", "In Review"),
            ("published", "Published"),
            ("archived", "Archived"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    parent_id = fields.Many2one(
        "ipai.doc",
        string="Parent Page",
        index=True,
    )
    child_ids = fields.One2many(
        "ipai.doc",
        "parent_id",
        string="Child Pages",
    )

    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
        tracking=True,
    )

    responsible_ids = fields.Many2many(
        "res.users",
        "ipai_doc_responsible_rel",
        "doc_id",
        "user_id",
        string="Collaborators",
    )

    tag_ids = fields.Many2many(
        "ipai.doc.tag",
        "ipai_doc_tag_rel",
        "doc_id",
        "tag_id",
        string="Tags",
    )

    body_json = fields.Json(
        string="Content (Blocks JSON)",
        help="Structured JSON representation of the document (blocks).",
    )

    body_html = fields.Html(
        string="Rendered Content",
        help="Rendered HTML version of the document content.",
    )

    is_template = fields.Boolean(
        string="Is Template?",
        default=False,
        help="Templates can be cloned when creating new docs.",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # Basic ACL helpers
    can_edit = fields.Boolean(
        string="User Can Edit",
        compute="_compute_can_edit",
    )

    @api.depends("owner_id", "responsible_ids")
    def _compute_can_edit(self):
        """
        Determine if current user can edit this document.

        Edit permission is granted to:
        - Document owner
        - Users listed as collaborators (responsible_ids)
        """
        user = self.env.user
        for doc in self:
            doc.can_edit = user == doc.owner_id or user in doc.responsible_ids

    def action_set_in_review(self):
        """
        Submit document for review.

        Transitions document from 'draft' to 'in_review' state,
        signaling it's ready for editorial review before publishing.
        """
        for doc in self:
            doc.state = "in_review"

    def action_publish(self):
        """
        Publish the document.

        Transitions to 'published' state, making the document
        visible to all users with read access.
        """
        for doc in self:
            doc.state = "published"

    def action_archive(self):
        """
        Archive the document.

        Transitions to 'archived' state, hiding the document from
        normal views while preserving it for reference.
        """
        for doc in self:
            doc.state = "archived"

    def copy(self, default=None):
        """
        Clone the document with appropriate defaults.

        Creates a copy with:
        - " (Copy)" suffix on name
        - Reset to 'draft' state
        - is_template set to False

        Args:
            default: Optional dict of field values to override

        Returns:
            New IpaiDoc record (copy of self)
        """
        default = dict(default or {})
        default.setdefault("name", _("%s (Copy)") % (self.name,))
        default.setdefault("state", "draft")
        default.setdefault("is_template", False)
        return super().copy(default)
