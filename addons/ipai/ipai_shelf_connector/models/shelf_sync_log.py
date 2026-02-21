"""Shelf Sync Log — audit trail for all sync operations."""

from odoo import fields, models


class ShelfSyncLog(models.Model):
    """Immutable log of Shelf.nu ↔ Odoo sync events."""

    _name = "shelf.sync.log"
    _description = "Shelf Sync Log"
    _order = "create_date desc"
    _log_access = True

    equipment_id = fields.Many2one(
        "maintenance.equipment",
        string="Equipment",
        ondelete="set null",
        index=True,
    )
    direction = fields.Selection(
        [
            ("odoo_to_shelf", "Odoo → Shelf"),
            ("shelf_to_odoo", "Shelf → Odoo"),
        ],
        required=True,
    )
    status = fields.Selection(
        [("success", "Success"), ("error", "Error")],
        required=True,
    )
    payload = fields.Text(string="Payload (JSON)")
    error_message = fields.Text(string="Error")
