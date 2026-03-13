# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class IpaiAiRunEvent(models.Model):
    """Detailed event log for AI runs."""

    _name = "ipai.ai.run.event"
    _description = "IPAI AI Run Event"
    _order = "create_date"

    run_id = fields.Many2one(
        comodel_name="ipai.ai.run",
        string="Run",
        required=True,
        ondelete="cascade",
        index=True,
    )
    event_type = fields.Selection(
        selection=[
            ("start", "Start"),
            ("rag", "RAG Retrieval"),
            ("llm", "LLM Call"),
            ("tool", "Tool Execution"),
            ("end", "End"),
            ("error", "Error"),
        ],
        string="Event Type",
        required=True,
    )
    payload = fields.Text(
        string="Payload",
        help="JSON payload with event details.",
    )
    create_date = fields.Datetime(
        string="Created At",
        readonly=True,
    )
