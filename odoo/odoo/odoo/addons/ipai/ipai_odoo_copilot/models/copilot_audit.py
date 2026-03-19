# -*- coding: utf-8 -*-

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CopilotAudit(models.Model):
    _name = "ipai.copilot.audit"
    _description = "Copilot Interaction Audit Log"
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
