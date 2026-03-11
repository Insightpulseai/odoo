# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiPermission(models.Model):
    """Permission scope model for granular access control."""

    _name = "ipai.permission"
    _description = "IPAI Permission Scope"
    _order = "scope_type, name"

    name = fields.Char(string="Name", required=True)
    scope_type = fields.Selection(
        [
            ("workspace", "Workspace"),
            ("space", "Space"),
            ("page", "Page"),
            ("database", "Database"),
        ],
        string="Scope Type",
        required=True,
    )
    scope_ref = fields.Reference(
        selection="_get_scope_models",
        string="Scope Reference",
    )
    role = fields.Selection(
        [
            ("admin", "Admin"),
            ("member", "Member"),
            ("guest", "Guest"),
        ],
        string="Role",
        required=True,
        default="member",
    )
    permission_level = fields.Selection(
        [
            ("view", "View"),
            ("comment", "Comment"),
            ("edit", "Edit"),
            ("manage", "Manage"),
        ],
        string="Permission Level",
        required=True,
        default="view",
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        ondelete="cascade",
    )
    group_id = fields.Many2one(
        "res.groups",
        string="Group",
        ondelete="cascade",
    )
    active = fields.Boolean(default=True)

    @api.model
    def _get_scope_models(self):
        """Return list of models that can be permission scopes."""
        return [
            ("ipai.workos.workspace", "Workspace"),
            ("ipai.workos.space", "Space"),
            ("ipai.workos.page", "Page"),
            ("ipai.workos.database", "Database"),
        ]

    def check_permission(self, user, required_level):
        """Check if user has required permission level."""
        level_order = ["view", "comment", "edit", "manage"]
        if self.permission_level not in level_order:
            return False
        if required_level not in level_order:
            return False
        current_idx = level_order.index(self.permission_level)
        required_idx = level_order.index(required_level)
        return current_idx >= required_idx


class IpaiShareToken(models.Model):
    """Share link token for controlled sharing."""

    _name = "ipai.share.token"
    _description = "IPAI Share Token"

    name = fields.Char(string="Token", required=True, readonly=True)
    scope_type = fields.Selection(
        [
            ("page", "Page"),
            ("database", "Database"),
        ],
        string="Scope Type",
        required=True,
    )
    scope_ref = fields.Reference(
        selection=[
            ("ipai.workos.page", "Page"),
            ("ipai.workos.database", "Database"),
        ],
        string="Shared Resource",
    )
    permission_level = fields.Selection(
        [
            ("view", "View"),
            ("comment", "Comment"),
            ("edit", "Edit"),
        ],
        string="Permission Level",
        required=True,
        default="view",
    )
    expires_at = fields.Datetime(string="Expires At")
    is_public = fields.Boolean(string="Public Link", default=False)
    created_by = fields.Many2one(
        "res.users",
        string="Created By",
        default=lambda self: self.env.user,
    )
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Generate unique token on create."""
        import secrets

        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = secrets.token_urlsafe(32)
        return super().create(vals_list)
