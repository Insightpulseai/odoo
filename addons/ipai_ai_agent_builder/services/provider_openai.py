# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiAiProviderOpenAI(models.AbstractModel):
    """OpenAI (ChatGPT) provider implementation."""

    _name = "ipai.ai.provider.openai"
    _inherit = "ipai.ai.provider.base"
    _description = "IPAI AI Provider - OpenAI"

    def get_api_key(self):
        """Get the OpenAI API key."""
        return self.env["res.config.settings"].get_openai_api_key()

    def generate(self, agent, prompt, tools=None):
        """Generate a response using OpenAI API.

        Args:
            agent: The ipai.ai.agent record
            prompt: The assembled prompt string
            tools: Optional list of tool definitions

        Returns:
            dict with 'content' and optional 'tool_calls'
        """
        api_key = self.get_api_key()
        if not api_key:
            raise UserError("OpenAI API key not configured. Set OPENAI_API_KEY or configure in settings.")

        try:
            import openai
        except ImportError:
            raise UserError("OpenAI Python package not installed. Run: pip install openai")

        client = openai.OpenAI(api_key=api_key)

        # Build messages
        messages = [{"role": "user", "content": prompt}]

        # Get tool definitions if the agent has tools
        tool_definitions = self._get_tool_definitions(agent) if not tools else tools

        # Build request kwargs
        kwargs = {
            "model": agent.model or "gpt-4o",
            "messages": messages,
            "temperature": agent.temperature,
            "max_tokens": agent.max_tokens,
        }

        # Add tools if available
        if tool_definitions:
            kwargs["tools"] = tool_definitions
            kwargs["tool_choice"] = "auto"

        try:
            response = client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            result = {
                "content": message.content or "",
                "tool_calls": [],
            }

            # Handle tool calls
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments),
                    })

            return result

        except openai.APIError as e:
            _logger.error(f"OpenAI API error: {e}")
            raise UserError(f"OpenAI API error: {e}")
        except Exception as e:
            _logger.exception("Error calling OpenAI API")
            raise UserError(f"Failed to generate response: {e}")
