# -*- coding: utf-8 -*-
from odoo import api, fields, models


class FocalboardBoard(models.Model):
    """Cached Focalboard board information."""

    _name = "ipai.focalboard.board"
    _description = "Focalboard Board"
    _order = "title"

    connector_id = fields.Many2one(
        "ipai.integration.connector",
        required=True,
        ondelete="cascade",
        domain="[('connector_type', '=', 'focalboard')]",
    )

    # Focalboard IDs
    fb_board_id = fields.Char(required=True, index=True)
    fb_workspace_id = fields.Char(index=True)

    # Board info
    title = fields.Char(required=True)
    description = fields.Text()
    board_type = fields.Selection(
        [
            ("board", "Board"),
            ("table", "Table"),
            ("gallery", "Gallery"),
            ("calendar", "Calendar"),
        ],
        default="board",
    )
    icon = fields.Char()

    # Linked Odoo project
    project_id = fields.Many2one(
        "project.project",
        string="Linked Project",
        help="Odoo project to sync cards with",
    )

    # Sync settings
    sync_enabled = fields.Boolean(default=False)
    sync_direction = fields.Selection(
        [
            ("fb_to_odoo", "Focalboard -> Odoo"),
            ("odoo_to_fb", "Odoo -> Focalboard"),
            ("bidirectional", "Bidirectional"),
        ],
        default="bidirectional",
    )
    last_sync = fields.Datetime()

    # Cards
    card_ids = fields.One2many("ipai.focalboard.card", "board_id", string="Cards")
    card_count = fields.Integer(compute="_compute_card_count")

    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "board_uniq",
            "unique(connector_id, fb_board_id)",
            "Board already exists for this connector!",
        ),
    ]

    def _compute_card_count(self):
        for rec in self:
            rec.card_count = len(rec.card_ids)

    @api.model
    def sync_boards(self, connector):
        """Sync boards from Focalboard API."""
        from ..services.focalboard_client import FocalboardClient

        client = FocalboardClient(connector)
        boards = client.get_boards(connector.fb_workspace_id)

        for board in boards:
            existing = self.search(
                [
                    ("connector_id", "=", connector.id),
                    ("fb_board_id", "=", board["id"]),
                ],
                limit=1,
            )

            vals = {
                "connector_id": connector.id,
                "fb_board_id": board["id"],
                "fb_workspace_id": board.get("teamId"),
                "title": board.get("title", "Untitled"),
                "description": board.get("description"),
                "icon": board.get("icon"),
                "last_sync": fields.Datetime.now(),
            }

            if existing:
                existing.write(vals)
            else:
                self.create(vals)

        return True

    def action_sync_cards(self):
        """Sync cards for this board."""
        self.ensure_one()
        return self.env["ipai.focalboard.card"].sync_cards(self)
