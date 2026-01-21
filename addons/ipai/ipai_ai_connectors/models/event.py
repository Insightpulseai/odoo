# -*- coding: utf-8 -*-
"""
IPAI AI Connectors - Event Model
================================

Stores inbound integration events from external systems like n8n, GitHub, Slack.
Provides audit trail and optional processing hooks.
"""
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiAiEvent(models.Model):
    """Inbound integration event record."""

    _name = "ipai.ai.event"
    _description = "IPAI AI Integration Event"
    _order = "create_date desc"
    _inherit = ["mail.thread"]

    # Source identification
    source = fields.Selection(
        [
            ("n8n", "n8n Workflow"),
            ("github", "GitHub"),
            ("slack", "Slack"),
            ("custom", "Custom"),
        ],
        required=True,
        index=True,
        tracking=True,
    )
    event_type = fields.Char(
        required=True,
        index=True,
        help="Event type identifier (e.g., issue.created, task.updated)",
    )
    ref = fields.Char(
        index=True,
        help="External reference ID from the source system",
    )

    # Payload storage
    payload_json = fields.Json(
        default=dict,
        help="Raw event payload from the source",
    )
    payload_text = fields.Text(
        compute="_compute_payload_text",
        string="Payload (Formatted)",
        help="JSON-formatted view of the payload for display",
    )

    # Processing state
    state = fields.Selection(
        [
            ("received", "Received"),
            ("processing", "Processing"),
            ("processed", "Processed"),
            ("failed", "Failed"),
            ("ignored", "Ignored"),
        ],
        default="received",
        required=True,
        index=True,
        tracking=True,
    )
    processed_date = fields.Datetime(
        readonly=True,
        help="When the event was processed",
    )
    error_message = fields.Text(
        help="Error message if processing failed",
    )

    # Metadata
    notes = fields.Text(
        help="Admin notes about this event",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends("payload_json")
    def _compute_payload_text(self):
        """Format payload as pretty JSON for display."""
        for rec in self:
            if rec.payload_json:
                try:
                    rec.payload_text = json.dumps(
                        rec.payload_json, indent=2, ensure_ascii=False
                    )
                except Exception:
                    rec.payload_text = str(rec.payload_json)
            else:
                rec.payload_text = "{}"

    def name_get(self):
        """Display name as source/event_type/ref."""
        result = []
        for rec in self:
            name = f"{rec.source}/{rec.event_type}"
            if rec.ref:
                name = f"{name}/{rec.ref}"
            result.append((rec.id, name))
        return result

    def action_mark_processed(self):
        """Mark event as processed."""
        self.write(
            {
                "state": "processed",
                "processed_date": fields.Datetime.now(),
            }
        )

    def action_mark_ignored(self):
        """Mark event as ignored (won't be processed)."""
        self.write(
            {
                "state": "ignored",
            }
        )

    def action_retry(self):
        """Reset event to received state for reprocessing."""
        self.write(
            {
                "state": "received",
                "error_message": False,
            }
        )

    @api.model
    def create_from_webhook(
        self, source, event_type, ref=None, payload=None, company_id=None
    ):
        """
        Create an event from webhook data.

        Args:
            source: Source identifier (n8n, github, slack, custom)
            event_type: Event type string
            ref: Optional external reference
            payload: Optional payload dict
            company_id: Optional company ID (defaults to main company)

        Returns:
            Created event record
        """
        # Normalize source
        source_map = {
            "n8n": "n8n",
            "github": "github",
            "slack": "slack",
        }
        normalized_source = source_map.get(str(source).lower(), "custom")

        # Get company
        if company_id:
            company = self.env["res.company"].browse(company_id)
        else:
            company = self.env.company

        # Create event
        event = self.sudo().create(
            {
                "source": normalized_source,
                "event_type": str(event_type) if event_type else "unknown",
                "ref": str(ref) if ref else False,
                "payload_json": payload or {},
                "company_id": company.id,
            }
        )

        _logger.info(
            "Created integration event: source=%s, type=%s, ref=%s, id=%d",
            normalized_source,
            event_type,
            ref,
            event.id,
        )

        return event
