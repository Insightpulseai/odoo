# -*- coding: utf-8 -*-

from odoo import fields, models


class IpaiAiAgent(models.Model):
    _name = "ipai.ai.agent"
    _description = "AI Agent"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )

    # Sources
    source_ids = fields.One2many(
        "ipai.ai.agent.source", "agent_id", string="Sources",
    )
    source_count = fields.Integer(
        compute="_compute_source_count", string="# Sources",
    )
    indexed_source_count = fields.Integer(
        compute="_compute_source_count", string="# Indexed",
    )
    restrict_to_sources = fields.Boolean(
        default=True,
        help="When enabled, the agent only uses active indexed sources "
             "as grounding context. When disabled, the agent may use "
             "general knowledge.",
    )

    # External identifiers (agent-platform / Foundry)
    external_agent_id = fields.Char(
        string="External Agent ID",
        help="Agent identifier in agent-platform or Foundry.",
    )

    def _compute_source_count(self):
        Source = self.env["ipai.ai.agent.source"]
        for agent in self:
            # Include inactive sources in total count
            all_sources = Source.with_context(active_test=False).search([
                ("agent_id", "=", agent.id),
            ])
            agent.source_count = len(all_sources)
            agent.indexed_source_count = len(
                all_sources.filtered(
                    lambda s: s.status == "indexed" and s.active
                )
            )

    def action_open_sources(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Agent Sources",
            "res_model": "ipai.ai.agent.source",
            "domain": [("agent_id", "=", self.id)],
            "view_mode": "list,form",
            "context": {"default_agent_id": self.id},
        }

    def action_test_agent(self):
        """Open the copilot chat panel scoped to this agent's sources."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Test Agent: %s" % self.name,
            "res_model": "ipai.ai.agent",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
            "context": {"test_agent_mode": True},
        }
