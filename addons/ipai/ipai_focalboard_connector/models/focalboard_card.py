# -*- coding: utf-8 -*-
from odoo import api, fields, models


class FocalboardCard(models.Model):
    """Cached Focalboard card (task) information."""

    _name = "ipai.focalboard.card"
    _description = "Focalboard Card"
    _order = "create_date desc"

    board_id = fields.Many2one(
        "ipai.focalboard.board",
        required=True,
        ondelete="cascade"
    )
    connector_id = fields.Many2one(
        related="board_id.connector_id",
        store=True
    )

    # Focalboard IDs
    fb_card_id = fields.Char(required=True, index=True)
    fb_parent_id = fields.Char(help="Parent card ID if nested")

    # Card info
    title = fields.Char(required=True)
    icon = fields.Char()

    # Properties (stored as JSON)
    properties_json = fields.Text(help="Card properties as JSON")

    # Linked Odoo task
    task_id = fields.Many2one(
        "project.task",
        string="Linked Task",
        help="Corresponding Odoo task"
    )

    # Sync status
    last_sync = fields.Datetime()
    sync_status = fields.Selection([
        ("synced", "Synced"),
        ("pending", "Pending Sync"),
        ("conflict", "Conflict"),
        ("error", "Error"),
    ], default="pending")
    sync_error = fields.Text()

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("card_uniq", "unique(board_id, fb_card_id)",
         "Card already exists for this board!"),
    ]

    @api.model
    def sync_cards(self, board):
        """Sync cards from Focalboard API."""
        from ..services.focalboard_client import FocalboardClient

        client = FocalboardClient(board.connector_id)
        cards = client.get_cards(board.fb_board_id)

        for card in cards:
            existing = self.search([
                ("board_id", "=", board.id),
                ("fb_card_id", "=", card["id"]),
            ], limit=1)

            vals = {
                "board_id": board.id,
                "fb_card_id": card["id"],
                "fb_parent_id": card.get("parentId"),
                "title": card.get("title", "Untitled"),
                "icon": card.get("icon"),
                "properties_json": str(card.get("fields", {})),
                "last_sync": fields.Datetime.now(),
                "sync_status": "synced",
            }

            if existing:
                existing.write(vals)
            else:
                self.create(vals)

        board.last_sync = fields.Datetime.now()
        return True

    def action_create_odoo_task(self):
        """Create a linked Odoo task from this card."""
        self.ensure_one()
        if self.task_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "project.task",
                "res_id": self.task_id.id,
                "view_mode": "form",
            }

        project = self.board_id.project_id
        if not project:
            project = self.env["project.project"].search([], limit=1)

        task = self.env["project.task"].create({
            "name": self.title,
            "project_id": project.id if project else False,
            "fb_card_id": self.fb_card_id,
        })
        self.task_id = task.id

        return {
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "res_id": task.id,
            "view_mode": "form",
        }
