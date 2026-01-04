# -*- coding: utf-8 -*-
"""IPAI Agent Run model - execution log with full audit trail."""

import json
import logging
from datetime import datetime

from odoo.exceptions import UserError

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiAgentRun(models.Model):
    """Agent run execution record with audit trail."""

    _name = "ipai.agent.run"
    _description = "IPAI Agent Run Log"
    _order = "create_date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(default=lambda self: self._generate_name(), tracking=True)
    skill_id = fields.Many2one(
        "ipai.agent.skill", required=True, tracking=True, ondelete="restrict"
    )
    skill_key = fields.Char(related="skill_id.key", store=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("running", "Running"),
            ("ok", "Completed"),
            ("failed", "Failed"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # Input/Output
    input_text = fields.Text(help="User prompt or input data")
    input_json = fields.Text(help="Structured input as JSON")
    output_text = fields.Text(help="Final output text")
    output_json = fields.Text(help="Structured output as JSON")

    # Execution trace
    tool_trace_json = fields.Text(help="JSON array of tool calls with inputs/outputs")
    error_text = fields.Text(help="Error message if failed")

    # Timing
    started_at = fields.Datetime()
    completed_at = fields.Datetime()
    duration_seconds = fields.Float(compute="_compute_duration", store=True)

    # User context
    user_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, tracking=True
    )

    def _generate_name(self):
        """Generate run name with timestamp."""
        return f"Run {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    @api.depends("started_at", "completed_at")
    def _compute_duration(self):
        for rec in self:
            if rec.started_at and rec.completed_at:
                delta = rec.completed_at - rec.started_at
                rec.duration_seconds = delta.total_seconds()
            else:
                rec.duration_seconds = 0.0

    def action_execute(self):
        """Execute the skill's workflow - deterministic tool chain."""
        for rec in self:
            rec._execute_workflow()
        return True

    def _execute_workflow(self):
        """Internal: run each tool in workflow_json order."""
        self.ensure_one()

        if self.state not in ("draft", "failed"):
            raise UserError("Can only execute runs in draft or failed state")

        self.write(
            {
                "state": "running",
                "started_at": fields.Datetime.now(),
                "error_text": False,
            }
        )

        trace = []
        Tool = self.env["ipai.agent.tool"]

        try:
            tool_keys = self.skill_id.get_workflow_tools()

            for tool_key in tool_keys:
                tool = Tool.search(
                    [("key", "=", tool_key), ("is_active", "=", True)], limit=1
                )

                if not tool:
                    raise UserError(f"Tool not found or inactive: {tool_key}")

                step = {
                    "tool": tool_key,
                    "started": fields.Datetime.now().isoformat(),
                    "result": None,
                    "error": None,
                }

                try:
                    # Execute tool (pass self as context via env)
                    self = self.with_context(agent_run_id=self.id)
                    result = tool.execute()
                    step["result"] = str(result) if result else "OK"
                except Exception as e:
                    step["error"] = str(e)
                    raise

                finally:
                    step["completed"] = fields.Datetime.now().isoformat()
                    trace.append(step)

            # Success
            self.write(
                {
                    "state": "ok",
                    "completed_at": fields.Datetime.now(),
                    "tool_trace_json": json.dumps(trace, ensure_ascii=False, indent=2),
                }
            )

        except Exception as e:
            _logger.exception("Agent run %s failed", self.id)
            self.write(
                {
                    "state": "failed",
                    "completed_at": fields.Datetime.now(),
                    "error_text": str(e),
                    "tool_trace_json": json.dumps(trace, ensure_ascii=False, indent=2),
                }
            )

    def action_reset_to_draft(self):
        """Reset failed run to draft for retry."""
        for rec in self:
            if rec.state == "failed":
                rec.write(
                    {
                        "state": "draft",
                        "started_at": False,
                        "completed_at": False,
                        "error_text": False,
                        "tool_trace_json": False,
                    }
                )
        return True

    def get_trace_list(self):
        """Parse and return tool trace as list of dicts."""
        self.ensure_one()
        try:
            return json.loads(self.tool_trace_json or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    def get_input_dict(self):
        """Parse and return input as dict."""
        self.ensure_one()
        try:
            return json.loads(self.input_json or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_output_dict(self):
        """Parse and return output as dict."""
        self.ensure_one()
        try:
            return json.loads(self.output_json or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}
