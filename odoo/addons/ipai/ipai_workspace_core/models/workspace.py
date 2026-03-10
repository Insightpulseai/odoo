# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, fields, models


class IpaiWorkspace(models.Model):
    """Extend ipai.workspace with collaborative workspace capabilities.

    Adds Notion-like features: icon, color theming, visibility controls,
    ownership, explicit membership with roles, and hierarchical pages.
    """

    _inherit = "ipai.workspace"

    icon = fields.Char(
        string="Icon",
        help="Emoji or icon name for the workspace",
    )
    color = fields.Integer(
        string="Color Index",
        default=0,
        help="Odoo color index (0-11) for kanban display",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        required=True,
        default=lambda self: self.env.user,
        index=True,
        help="Primary owner of this workspace",
    )
    member_ids = fields.Many2many(
        "res.users",
        "ipai_workspace_core_member_rel",
        "workspace_id",
        "user_id",
        string="Members",
        help="Users with access to this workspace (quick-add)",
    )
    visibility = fields.Selection(
        [
            ("private", "Private"),
            ("team", "Team"),
            ("public", "Public"),
        ],
        string="Visibility",
        default="team",
        required=True,
        help="Controls who can see this workspace",
    )
    page_ids = fields.One2many(
        "ipai.workspace.page",
        "workspace_id",
        string="Pages",
    )
    workspace_member_ids = fields.One2many(
        "ipai.workspace.member",
        "workspace_id",
        string="Membership Roles",
        help="Explicit membership with role-based permissions",
    )

    def action_add_member(self, user_id):
        """Add a user to this workspace's member list.

        :param int user_id: ID of the res.users record to add
        """
        self.ensure_one()
        user = self.env["res.users"].browse(user_id)
        if user.exists() and user not in self.member_ids:
            self.write({"member_ids": [(4, user_id)]})

    def action_remove_member(self, user_id):
        """Remove a user from this workspace's member list.

        :param int user_id: ID of the res.users record to remove
        """
        self.ensure_one()
        self.write({"member_ids": [(3, user_id)]})
