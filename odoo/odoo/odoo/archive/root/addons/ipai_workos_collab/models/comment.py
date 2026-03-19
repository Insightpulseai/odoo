# -*- coding: utf-8 -*-
import re

from odoo import api, fields, models


class IpaiWorkosComment(models.Model):
    """Comment - Discussion threads on pages/rows."""

    _name = "ipai.workos.comment"
    _description = "Work OS Comment"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    # Target (polymorphic reference)
    target_model = fields.Char(string="Target Model", required=True, index=True)
    target_id = fields.Integer(string="Target ID", required=True, index=True)
    target_name = fields.Char(string="Target Name", compute="_compute_target_name")

    # Content
    content = fields.Html(string="Comment", required=True)
    content_text = fields.Text(
        string="Plain Text",
        compute="_compute_content_text",
        store=True,
    )

    # Thread structure
    parent_id = fields.Many2one(
        "ipai.workos.comment",
        string="Parent Comment",
        ondelete="cascade",
    )
    child_ids = fields.One2many(
        "ipai.workos.comment",
        "parent_id",
        string="Replies",
    )
    reply_count = fields.Integer(
        string="Replies",
        compute="_compute_reply_count",
    )

    # Anchor (for inline comments)
    anchor_block_id = fields.Integer(
        string="Anchor Block ID",
        help="Block ID where comment is anchored (for inline comments)",
    )

    # Author
    author_id = fields.Many2one(
        "res.users",
        string="Author",
        default=lambda self: self.env.user,
        required=True,
    )

    # Mentions
    mentioned_user_ids = fields.Many2many(
        "res.users",
        "workos_comment_mention_rel",
        "comment_id",
        "user_id",
        string="Mentioned Users",
    )

    # Status
    is_resolved = fields.Boolean(string="Resolved", default=False)
    resolved_by = fields.Many2one("res.users", string="Resolved By")
    resolved_at = fields.Datetime(string="Resolved At")

    def _compute_target_name(self):
        for record in self:
            try:
                target = self.env[record.target_model].browse(record.target_id)
                record.target_name = (
                    target.display_name if target.exists() else "Deleted"
                )
            except Exception:
                record.target_name = "Unknown"

    @api.depends("content")
    def _compute_content_text(self):
        for record in self:
            # Strip HTML tags
            text = re.sub(r"<[^>]+>", "", record.content or "")
            record.content_text = text.strip()

    @api.depends("child_ids")
    def _compute_reply_count(self):
        for record in self:
            record.reply_count = len(record.child_ids)

    @api.model_create_multi
    def create(self, vals_list):
        """Process mentions on create."""
        records = super().create(vals_list)
        for record in records:
            record._process_mentions()
        return records

    def write(self, vals):
        """Process mentions on content update."""
        result = super().write(vals)
        if "content" in vals:
            self._process_mentions()
        return result

    def _process_mentions(self):
        """Extract @mentions from content and notify users."""
        for record in self:
            # Find @mentions in content
            mentions = re.findall(r"@(\w+)", record.content_text or "")
            if not mentions:
                continue

            # Find matching users
            users = self.env["res.users"].search([("login", "in", mentions)])
            if users:
                record.mentioned_user_ids = [(6, 0, users.ids)]
                record._notify_mentioned_users(users)

    def _notify_mentioned_users(self, users):
        """Send notifications to mentioned users."""
        for user in users:
            if user.partner_id:
                self.message_post(
                    body=f"You were mentioned in a comment by {self.author_id.name}",
                    partner_ids=[user.partner_id.id],
                    message_type="notification",
                )

    def action_resolve(self):
        """Mark comment as resolved."""
        self.write(
            {
                "is_resolved": True,
                "resolved_by": self.env.user.id,
                "resolved_at": fields.Datetime.now(),
            }
        )

    def action_unresolve(self):
        """Mark comment as unresolved."""
        self.write(
            {
                "is_resolved": False,
                "resolved_by": False,
                "resolved_at": False,
            }
        )

    @api.model
    def get_comments_for_target(self, target_model, target_id, include_resolved=False):
        """Get all comments for a target."""
        domain = [
            ("target_model", "=", target_model),
            ("target_id", "=", target_id),
            ("parent_id", "=", False),  # Only root comments
        ]
        if not include_resolved:
            domain.append(("is_resolved", "=", False))
        return self.search(domain, order="create_date desc")
