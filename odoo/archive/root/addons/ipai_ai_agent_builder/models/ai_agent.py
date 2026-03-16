# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiAiAgent(models.Model):
    """AI Agent definition with system prompt and provider configuration."""

    _name = "ipai.ai.agent"
    _description = "IPAI AI Agent"
    _order = "name"

    name = fields.Char(
        string="Name",
        required=True,
        index=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    system_prompt = fields.Text(
        string="System Prompt",
        help="The system prompt that defines the agent's behavior and persona.",
    )
    style = fields.Selection(
        selection=[
            ("professional", "Professional"),
            ("friendly", "Friendly"),
            ("concise", "Concise"),
            ("detailed", "Detailed"),
        ],
        string="Response Style",
        default="professional",
        help="The communication style for agent responses.",
    )
    provider = fields.Selection(
        selection=[
            ("openai", "OpenAI (ChatGPT)"),
            ("google", "Google (Gemini)"),
        ],
        string="LLM Provider",
        default="openai",
        required=True,
    )
    model = fields.Char(
        string="Model",
        default="gpt-4o",
        help="The specific model to use (e.g., gpt-4o, gemini-pro).",
    )
    temperature = fields.Float(
        string="Temperature",
        default=0.7,
        help="Controls randomness in responses (0.0 = deterministic, 1.0 = creative).",
    )
    max_tokens = fields.Integer(
        string="Max Tokens",
        default=2048,
        help="Maximum number of tokens in the response.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )
    topic_ids = fields.One2many(
        comodel_name="ipai.ai.topic",
        inverse_name="agent_id",
        string="Topics",
    )
    source_ids = fields.One2many(
        comodel_name="ipai.ai.source",
        inverse_name="agent_id",
        string="Sources",
    )
    run_ids = fields.One2many(
        comodel_name="ipai.ai.run",
        inverse_name="agent_id",
        string="Runs",
    )
    run_count = fields.Integer(
        string="Run Count",
        compute="_compute_run_count",
    )

    @api.depends("run_ids")
    def _compute_run_count(self):
        for agent in self:
            agent.run_count = len(agent.run_ids)

    def get_all_tools(self):
        """Get all tools available to this agent via its topics."""
        self.ensure_one()
        tools = self.env["ipai.ai.tool"]
        for topic in self.topic_ids:
            tools |= topic.tool_ids
        return tools

    def get_provider_service(self):
        """Get the LLM provider service for this agent."""
        self.ensure_one()
        if self.provider == "openai":
            return self.env["ipai.ai.provider.openai"]
        elif self.provider == "google":
            return self.env["ipai.ai.provider.google"]
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def chat(self, message, context=None):
        """Process a chat message and return the response."""
        self.ensure_one()
        context = context or {}

        # Create a new run
        run = self.env["ipai.ai.run"].create({
            "agent_id": self.id,
            "user_id": self.env.uid,
            "input": message,
        })

        try:
            # Log start event
            run.log_event("start", {"message": message, "context": context})

            # Retrieve relevant context via RAG
            rag_service = self.env["ipai.ai.retrieval.service"]
            rag_context = rag_service.retrieve_context(self, message)
            run.log_event("rag", {"chunks_retrieved": len(rag_context)})

            # Build prompt with RAG context
            prompt = self._build_prompt(message, rag_context)

            # Get provider and generate response
            provider = self.get_provider_service()
            import time
            start_time = time.time()
            response = provider.generate(self, prompt)
            latency_ms = int((time.time() - start_time) * 1000)

            run.log_event("llm", {
                "provider": self.provider,
                "model": self.model,
                "latency_ms": latency_ms,
            })

            # Handle tool calls if present
            tool_calls = []
            if response.get("tool_calls"):
                tool_executor = self.env["ipai.ai.tool.executor"]
                for tool_call in response["tool_calls"]:
                    result = tool_executor.execute(
                        run=run,
                        tool_key=tool_call["name"],
                        input_json=tool_call["arguments"],
                    )
                    tool_calls.append(result)

            # Update run with response
            run.write({
                "output": response.get("content", ""),
                "provider": self.provider,
                "model": self.model,
                "latency_ms": latency_ms,
            })
            run.log_event("end", {"status": "success"})

            return {
                "run_id": run.id,
                "response": response.get("content", ""),
                "tool_calls": tool_calls,
                "sources": [
                    {"chunk_id": c["id"], "score": c["score"]}
                    for c in rag_context
                ],
            }

        except Exception as e:
            _logger.exception("Error in agent chat")
            run.log_event("error", {"error": str(e)})
            run.write({"output": f"Error: {str(e)}"})
            raise

    def _build_prompt(self, message, rag_context):
        """Build the full prompt including system, topics, RAG context, and user message."""
        self.ensure_one()
        parts = []

        # System prompt
        if self.system_prompt:
            parts.append(f"System: {self.system_prompt}")

        # Style instruction
        style_instructions = {
            "professional": "Respond in a professional, business-appropriate manner.",
            "friendly": "Respond in a warm, approachable, and friendly manner.",
            "concise": "Respond briefly and to the point, avoiding unnecessary elaboration.",
            "detailed": "Provide thorough, detailed responses with examples when helpful.",
        }
        if self.style and self.style in style_instructions:
            parts.append(f"Style: {style_instructions[self.style]}")

        # Topic instructions
        for topic in self.topic_ids:
            if topic.instructions:
                parts.append(f"Topic ({topic.name}): {topic.instructions}")

        # RAG context
        if rag_context:
            context_text = "\n\n".join([
                f"[Source {i+1}]: {c['content']}"
                for i, c in enumerate(rag_context[:5])  # Limit to top 5
            ])
            parts.append(f"Relevant Context:\n{context_text}")

        # User message
        parts.append(f"User: {message}")

        return "\n\n".join(parts)
