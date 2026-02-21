"""Plane Sync Log — audit trail for all sync operations."""

from odoo import fields, models


class PlaneSyncLog(models.Model):
    """Immutable log of Plane ↔ Odoo sync events."""

    _name = "plane.sync.log"
    _description = "Plane Sync Log"
    _order = "create_date desc"
    _log_access = True

    task_id = fields.Many2one(
        "project.task", string="Task", ondelete="set null", index=True,
    )
    direction = fields.Selection(
        [
            ("odoo_to_plane", "Odoo → Plane"),
            ("plane_to_odoo", "Plane → Odoo"),
        ],
        required=True,
    )
    status = fields.Selection(
        [("success", "Success"), ("error", "Error")],
        required=True,
    )
    payload = fields.Text(string="Payload (JSON)")
    error_message = fields.Text(string="Error")
