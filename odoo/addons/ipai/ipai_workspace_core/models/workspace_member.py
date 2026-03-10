# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, fields, models


class IpaiWorkspaceMember(models.Model):
    """Explicit workspace membership with role-based permissions.

    Provides fine-grained access control beyond the simple Many2many
    relationship on ipai.workspace.member_ids.
    """

    _name = "ipai.workspace.member"
    _description = "Workspace Member"
    _order = "workspace_id, user_id"

    workspace_id = fields.Many2one(
        "ipai.workspace",
        string="Workspace",
        required=True,
        ondelete="cascade",
        index=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        index=True,
    )
    role = fields.Selection(
        [
            ("viewer", "Viewer"),
            ("editor", "Editor"),
            ("admin", "Admin"),
        ],
        string="Role",
        default="editor",
        required=True,
    )

    _sql_constraints = [
        (
            "workspace_user_unique",
            "UNIQUE(workspace_id, user_id)",
            "A user can only have one membership per workspace.",
        ),
    ]
