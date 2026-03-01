# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Plane webhook delivery tracking for deduplication.

Each inbound Plane webhook request carries a unique delivery ID.  This
model stores those IDs so that downstream handlers can skip duplicates
(e.g. retried deliveries after transient failures).

A daily cron (``ir_cron_plane_webhook_cleanup``) purges records older
than 7 days.
"""

from odoo import fields, models


class PlaneWebhookDelivery(models.Model):
    _name = "plane.webhook.delivery"
    _description = "Plane Webhook Delivery (dedup ledger)"
    _order = "received_at desc"

    delivery_id = fields.Char(
        string="Delivery ID",
        required=True,
        index=True,
        help="Unique identifier from the Plane webhook request headers.",
    )
    event_type = fields.Char(
        string="Event Type",
        help="Webhook event type (e.g. issue.created, cycle.updated).",
    )
    received_at = fields.Datetime(
        string="Received At",
        default=fields.Datetime.now,
        required=True,
    )
    processed = fields.Boolean(
        string="Processed",
        default=False,
        help="Set to True once downstream handler has processed this event.",
    )
    error = fields.Text(
        string="Error",
        help="Error details if processing failed.",
    )

    _sql_constraints = [
        (
            "delivery_id_unique",
            "UNIQUE(delivery_id)",
            "Duplicate delivery ID",
        ),
    ]
