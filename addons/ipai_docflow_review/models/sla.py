from datetime import timedelta

from odoo import _, api, fields, models


class DocflowSlaEvent(models.Model):
    _name = "docflow.sla.event"
    _description = "DocFlow SLA Event"
    _order = "create_date desc"

    document_id = fields.Many2one("docflow.document", required=True, ondelete="cascade")
    event_type = fields.Selection(
        [
            ("assigned", "Assigned"),
            ("breach", "Breach"),
            ("escalated", "Escalated"),
            ("resolved", "Resolved"),
        ],
        required=True,
    )
    note = fields.Char()
