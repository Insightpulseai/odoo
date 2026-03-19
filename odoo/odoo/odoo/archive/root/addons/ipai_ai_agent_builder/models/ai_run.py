# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import json

from odoo import api, fields, models


class IpaiAiRun(models.Model):
    """Conversation run tracking for observability."""

    _name = "ipai.ai.run"
    _description = "IPAI AI Run"
    _order = "create_date desc"

    agent_id = fields.Many2one(
        comodel_name="ipai.ai.agent",
        string="Agent",
        required=True,
        ondelete="cascade",
        index=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        default=lambda self: self.env.uid,
        index=True,
    )
    input = fields.Text(
        string="Input",
        help="The user's input message.",
    )
    output = fields.Text(
        string="Output",
        help="The agent's response.",
    )
    provider = fields.Char(
        string="Provider",
        help="The LLM provider used for this run.",
    )
    model = fields.Char(
        string="Model",
        help="The specific model used for this run.",
    )
    latency_ms = fields.Integer(
        string="Latency (ms)",
        help="Total response time in milliseconds.",
    )
    event_ids = fields.One2many(
        comodel_name="ipai.ai.run.event",
        inverse_name="run_id",
        string="Events",
    )
    tool_call_ids = fields.One2many(
        comodel_name="ipai.ai.tool.call",
        inverse_name="run_id",
        string="Tool Calls",
    )
    company_id = fields.Many2one(
        related="agent_id.company_id",
        string="Company",
        store=True,
    )

    def log_event(self, event_type, payload=None):
        """Log an event for this run."""
        self.ensure_one()
        self.env["ipai.ai.run.event"].create({
            "run_id": self.id,
            "event_type": event_type,
            "payload": json.dumps(payload) if payload else False,
        })

    @api.model
    def get_recent_runs(self, agent_id=None, limit=10):
        """Get recent runs, optionally filtered by agent."""
        domain = []
        if agent_id:
            domain.append(("agent_id", "=", agent_id))
        return self.search(domain, limit=limit, order="create_date desc")
