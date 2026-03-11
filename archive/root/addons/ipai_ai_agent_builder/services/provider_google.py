# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiAiProviderGoogle(models.AbstractModel):
    """Google (Gemini) provider implementation."""

    _name = "ipai.ai.provider.google"
    _inherit = "ipai.ai.provider.base"
    _description = "IPAI AI Provider - Google"

    def get_api_key(self):
        """Get the Google API key."""
        return self.env["res.config.settings"].get_google_api_key()

    def generate(self, agent, prompt, tools=None):
        """Generate a response using Google Gemini API.

        Args:
            agent: The ipai.ai.agent record
            prompt: The assembled prompt string
            tools: Optional list of tool definitions

        Returns:
            dict with 'content' and optional 'tool_calls'
        """
        api_key = self.get_api_key()
        if not api_key:
            raise UserError("Google API key not configured. Set GOOGLE_API_KEY or configure in settings.")

        try:
            import google.generativeai as genai
        except ImportError:
            raise UserError("Google Generative AI package not installed. Run: pip install google-generativeai")

        genai.configure(api_key=api_key)

        # Determine model
        model_name = agent.model or "gemini-pro"
        if not model_name.startswith("gemini"):
            model_name = "gemini-pro"  # Default fallback for Gemini

        # Create model
        generation_config = genai.GenerationConfig(
            temperature=agent.temperature,
            max_output_tokens=agent.max_tokens,
        )

        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
        )

        # Get tool definitions and convert to Gemini format
        tool_definitions = self._get_tool_definitions(agent) if not tools else tools
        gemini_tools = self._convert_tools_to_gemini_format(tool_definitions) if tool_definitions else None

        try:
            # Generate response
            if gemini_tools:
                response = model.generate_content(
                    prompt,
                    tools=gemini_tools,
                )
            else:
                response = model.generate_content(prompt)

            result = {
                "content": "",
                "tool_calls": [],
            }

            # Extract text content
            if response.text:
                result["content"] = response.text

            # Handle function calls (Gemini's equivalent of tool calls)
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, "function_call"):
                            fc = part.function_call
                            result["tool_calls"].append({
                                "id": f"call_{fc.name}",
                                "name": fc.name,
                                "arguments": dict(fc.args) if fc.args else {},
                            })
                        elif hasattr(part, "text"):
                            result["content"] = part.text

            return result

        except Exception as e:
            _logger.exception("Error calling Google Gemini API")
            raise UserError(f"Failed to generate response: {e}")

    def _convert_tools_to_gemini_format(self, openai_tools):
        """Convert OpenAI-format tool definitions to Gemini format.

        Args:
            openai_tools: List of tool definitions in OpenAI format

        Returns:
            Gemini-compatible tool definitions
        """
        try:
            import google.generativeai as genai
        except ImportError:
            return None

        gemini_functions = []
        for tool in openai_tools:
            if tool.get("type") == "function":
                func = tool["function"]
                gemini_func = genai.protos.FunctionDeclaration(
                    name=func["name"],
                    description=func.get("description", ""),
                    parameters=self._convert_schema_to_gemini(func.get("parameters", {})),
                )
                gemini_functions.append(gemini_func)

        if gemini_functions:
            return [genai.protos.Tool(function_declarations=gemini_functions)]
        return None

    def _convert_schema_to_gemini(self, schema):
        """Convert JSON Schema to Gemini parameter format.

        Args:
            schema: JSON Schema dict

        Returns:
            Gemini-compatible schema
        """
        try:
            import google.generativeai as genai
        except ImportError:
            return None

        if not schema:
            return None

        # Map JSON Schema types to Gemini types
        type_map = {
            "string": genai.protos.Type.STRING,
            "number": genai.protos.Type.NUMBER,
            "integer": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT,
        }

        schema_type = schema.get("type", "object")
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        gemini_properties = {}
        for prop_name, prop_schema in properties.items():
            prop_type = prop_schema.get("type", "string")
            gemini_properties[prop_name] = genai.protos.Schema(
                type=type_map.get(prop_type, genai.protos.Type.STRING),
                description=prop_schema.get("description", ""),
            )

        return genai.protos.Schema(
            type=type_map.get(schema_type, genai.protos.Type.OBJECT),
            properties=gemini_properties,
            required=required,
        )
