# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IPAIAIAgent(models.Model):
    _name = "ipai.ai.agent"
    _description = "AI Agent"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    enabled = fields.Boolean(default=True, help="If disabled, agent won't appear in Ask AI panel")
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=False,
        help="Leave empty for global agent available to all companies"
    )

    provider = fields.Selection(
        [
            ("openai_compat", "OpenAI-Compatible"),
            ("anthropic", "Anthropic Claude"),
            ("local", "Local (Ollama/vLLM)"),
        ],
        default="openai_compat",
        required=True,
    )
    model = fields.Char(default="gpt-4o-mini", help="Model identifier (e.g., gpt-4o, claude-3-sonnet)")

    system_prompt = fields.Text(
        default=lambda self: self._default_system_prompt(),
        help="System instructions for the agent"
    )

    # Tool policies
    allowed_models_json = fields.Json(default=list, help="List of allowed model names")
    allowed_tools_json = fields.Json(default=list, help="List of allowed tool names")
    read_only = fields.Boolean(
        default=True,
        help="If checked, agent can only read data (open views/reports, search_read)"
    )

    # Statistics
    thread_count = fields.Integer(compute="_compute_thread_count", string="Conversations")

    def _default_system_prompt(self):
        return (
            "You are an in-product help assistant for this Odoo instance.\n"
            "Rules:\n"
            "- Use the provided evidence snippets when answering.\n"
            "- Cite sources for any factual claim using the citation list.\n"
            "- If evidence is insufficient, say you don't know and ask a clarifying question.\n"
            "- Never invent URLs or citations.\n"
            "- Be concise and helpful.\n"
        )

    @api.depends()
    def _compute_thread_count(self):
        Thread = self.env["ipai.ai.thread"]
        for rec in self:
            rec.thread_count = Thread.search_count([("agent_id", "=", rec.id)])

    @api.model
    def ensure_default_agent(self):
        """Ensure a default 'Ask AI' agent exists for the current company."""
        agent = self.search([
            ("name", "=", "Ask AI"),
            "|", ("company_id", "=", self.env.company.id), ("company_id", "=", False)
        ], limit=1)
        if not agent:
            agent = self.create({
                "name": "Ask AI",
                "company_id": False,  # Global
            })
        return agent

    def action_view_threads(self):
        """Open threads for this agent."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Conversations - {self.name}",
            "res_model": "ipai.ai.thread",
            "view_mode": "tree,form",
            "domain": [("agent_id", "=", self.id)],
            "context": {"default_agent_id": self.id},
        }
