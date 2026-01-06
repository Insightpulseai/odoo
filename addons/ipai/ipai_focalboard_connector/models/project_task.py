# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTask(models.Model):
    """Extend project.task with Focalboard link."""

    _inherit = "project.task"

    fb_card_id = fields.Char(
        string="Focalboard Card ID",
        help="Linked Focalboard card ID",
        index=True
    )
    fb_board_id = fields.Many2one(
        "ipai.focalboard.board",
        string="Focalboard Board",
        compute="_compute_fb_board",
        store=True
    )
    fb_sync_enabled = fields.Boolean(
        string="Sync to Focalboard",
        default=False
    )

    @api.depends("fb_card_id")
    def _compute_fb_board(self):
        Card = self.env["ipai.focalboard.card"]
        for task in self:
            if task.fb_card_id:
                card = Card.search([
                    ("fb_card_id", "=", task.fb_card_id)
                ], limit=1)
                task.fb_board_id = card.board_id if card else False
            else:
                task.fb_board_id = False

    def action_sync_to_focalboard(self):
        """Sync this task to Focalboard as a card."""
        self.ensure_one()
        if not self.project_id:
            return

        # Find linked board
        board = self.env["ipai.focalboard.board"].search([
            ("project_id", "=", self.project_id.id),
            ("sync_enabled", "=", True),
        ], limit=1)

        if not board:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "No Board Linked",
                    "message": "No Focalboard board is linked to this project.",
                    "type": "warning",
                }
            }

        from ..services.focalboard_client import FocalboardClient
        client = FocalboardClient(board.connector_id)

        if self.fb_card_id:
            # Update existing card
            client.update_card(self.fb_card_id, {"title": self.name})
        else:
            # Create new card
            result = client.create_card(board.fb_board_id, {
                "title": self.name,
            })
            if result:
                self.fb_card_id = result.get("id")

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Synced",
                "message": "Task synced to Focalboard.",
                "type": "success",
            }
        }
