# -*- coding: utf-8 -*-

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CopilotAudit(models.Model):
    _name = "ipai.copilot.audit"
    _description = "Pulser Interaction Audit Log"
    _order = "create_date desc"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.uid,
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        readonly=True,
        help="Company context at the time of the interaction",
    )
    prompt = fields.Text(string="Prompt", readonly=True)
    response_excerpt = fields.Text(
        string="Response Excerpt",
        readonly=True,
        help="First 500 characters of the response",
    )
    environment_mode = fields.Selection(
        [("read_only", "Read-Only"), ("full", "Full Access")],
        string="Mode",
        readonly=True,
    )
    blocked = fields.Boolean(string="Blocked", readonly=True, default=False)
    reason = fields.Char(string="Reason", readonly=True)
    source = fields.Selection(
        [("discuss", "Discuss Bot"), ("api", "HTTP API"), ("widget", "Web Widget")],
        string="Source",
        readonly=True,
    )
    surface = fields.Selection(
        [
            ("web", "Web"),
            ("erp", "ERP"),
            ("copilot", "Copilot"),
            ("analytics", "Analytics"),
            ("ops", "Ops"),
        ],
        string="Surface",
        readonly=True,
        help="Calling application surface",
    )
    app_roles = fields.Char(
        string="App Roles",
        readonly=True,
        help="Comma-separated application roles at time of request",
    )
    context_envelope = fields.Text(
        string="Context Envelope",
        readonly=True,
        help="JSON-serialized context envelope injected into the request",
    )

    # --- Extended audit fields (v2.0.0) ---

    skill_id = fields.Char(
        string="Skill",
        readonly=True,
        help="Skill pack selected by the intent router",
    )
    skill_confidence = fields.Selection(
        [("high", "High"), ("medium", "Medium"), ("low", "Low")],
        string="Confidence",
        readonly=True,
        help="Router confidence in skill classification",
    )
    tools_invoked = fields.Char(
        string="Tools Invoked",
        readonly=True,
        help="Comma-separated list of tools the agent called",
    )
    knowledge_source = fields.Selection(
        [
            ("odoo", "Odoo ORM"),
            ("search", "AI Search"),
            ("fabric", "Fabric SQL"),
            ("mixed", "Multiple Sources"),
            ("none", "No Tools"),
        ],
        string="Knowledge Source",
        readonly=True,
        help="Primary knowledge source used to answer",
    )
    write_proposal_queued = fields.Boolean(
        string="Write Proposed",
        readonly=True,
        default=False,
        help="Whether a write action was queued via propose_action",
    )
    response_disposition = fields.Selection(
        [
            ("answered", "Answered"),
            ("blocked", "Blocked"),
            ("queued", "Write Queued"),
            ("fallback", "Fallback Response"),
            ("error", "Error"),
        ],
        string="Disposition",
        readonly=True,
        help="How the request was ultimately resolved",
    )
    foundry_mode = fields.Selection(
        [("sdk", "SDK"), ("http", "HTTP"), ("simple", "Simple Completion"),
         ("offline", "Offline Fallback")],
        string="Foundry Mode",
        readonly=True,
        help="Which Foundry communication path was used",
    )
    latency_ms = fields.Integer(
        string="Latency (ms)",
        readonly=True,
        help="End-to-end response latency in milliseconds",
    )
