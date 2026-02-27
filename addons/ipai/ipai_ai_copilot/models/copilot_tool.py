"""
ipai.copilot.tool — Extensible tool registry.

Tools are what the AI copilot can DO (not just say).
Each tool maps to a Python function in copilot.py::_execute_tool_confirmed.
Tool declarations are sent to Gemini as function_declarations in the bridge payload.

Adding a new tool requires:
  1. Create a record in this model (via data XML or admin UI)
  2. Implement the tool in controllers/copilot.py::_execute_tool_confirmed
  3. Add preview logic in controllers/copilot.py::_dispatch_tool_preview
"""
import json
from odoo import models, fields


class IpaiCopilotTool(models.Model):
    _name = "ipai.copilot.tool"
    _description = "IPAI Copilot Tool"
    _order = "category, name"

    name = fields.Char(
        required=True,
        help="snake_case identifier, must match key in _execute_tool_confirmed",
    )
    display_name = fields.Char(required=True)
    description = fields.Text(
        required=True,
        help="Human-readable description of what this tool does. Sent to the AI as the function description.",
    )
    category = fields.Selection(
        [
            ("navigation", "Navigation"),
            ("read", "Read Data"),
            ("write", "Write Data (requires confirmation)"),
            ("automation", "Automation"),
            ("analysis", "Analysis"),
        ],
        required=True,
        default="read",
    )
    parameters_json = fields.Text(
        default="{}",
        help="JSON Schema (draft-07) describing the tool's parameters. Must be valid JSON.",
    )
    active = fields.Boolean(default=True)
    requires_confirmation = fields.Boolean(
        default=False,
        help="If True, the UI MUST show a confirmation dialog before executing this tool.",
    )

    def _to_gemini_declaration(self):
        """Convert to Gemini function calling declaration format (Gemini API spec)."""
        try:
            params = json.loads(self.parameters_json or "{}")
        except (json.JSONDecodeError, TypeError):
            params = {}
        return {
            "name": self.name,
            "description": self.description,
            "parameters": params,
        }
