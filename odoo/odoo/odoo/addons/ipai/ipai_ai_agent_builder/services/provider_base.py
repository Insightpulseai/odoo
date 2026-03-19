# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo import models


class IpaiAiProviderBase(models.AbstractModel):
    """Base class for LLM providers."""

    _name = "ipai.ai.provider.base"
    _description = "IPAI AI Provider Base"

    def generate(self, agent, prompt, tools=None):
        """Generate a response from the LLM.

        Args:
            agent: The ipai.ai.agent record
            prompt: The assembled prompt string
            tools: Optional list of tool definitions

        Returns:
            dict with 'content' and optional 'tool_calls'
        """
        raise NotImplementedError("Subclasses must implement generate()")

    def get_api_key(self):
        """Get the API key for this provider.

        Returns:
            str: API key
        """
        raise NotImplementedError("Subclasses must implement get_api_key()")

    def _get_tool_definitions(self, agent):
        """Get tool definitions for function calling.

        Args:
            agent: The ipai.ai.agent record

        Returns:
            list of tool definitions in provider-specific format
        """
        tools = agent.get_all_tools()
        return [tool.get_llm_definition() for tool in tools if tool.active]
