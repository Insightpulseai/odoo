# -*- coding: utf-8 -*-
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SkillExecution(models.Model):
    _name = "ipai.skill.execution"
    _description = "Agent Skill Execution Log"
    _order = "create_date desc"
    _rec_name = "display_name"

    skill_id = fields.Many2one(
        "ipai.skill.definition",
        string="Skill",
        required=True,
        ondelete="cascade",
        index=True,
    )
    display_name = fields.Char(compute="_compute_display_name", store=True)
    state = fields.Selection(
        [
            ("queued", "Queued"),
            ("running", "Running"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        default="queued",
        required=True,
        index=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Executed By",
        default=lambda self: self.env.user,
        required=True,
    )
    input_data = fields.Text(help="JSON input payload")
    output_data = fields.Text(help="JSON output result")
    error_message = fields.Text()
    duration_seconds = fields.Float(help="Execution duration in seconds")
    started_at = fields.Datetime()
    completed_at = fields.Datetime()

    # Tool execution log
    tool_log = fields.Text(
        help="JSON array of tool execution results in workflow order"
    )

    @api.depends("skill_id.name", "create_date")
    def _compute_display_name(self):
        for rec in self:
            skill_name = rec.skill_id.name or "Unknown"
            date_str = (
                rec.create_date.strftime("%Y-%m-%d %H:%M")
                if rec.create_date
                else "Draft"
            )
            rec.display_name = f"{skill_name} — {date_str}"

    def action_start(self):
        """Mark execution as running."""
        self.write({"state": "running", "started_at": fields.Datetime.now()})

    def action_complete(self, output_data=None):
        """Mark execution as completed with results."""
        vals = {
            "state": "completed",
            "completed_at": fields.Datetime.now(),
        }
        if output_data:
            vals["output_data"] = json.dumps(output_data)
        if self.started_at:
            delta = fields.Datetime.now() - self.started_at
            vals["duration_seconds"] = delta.total_seconds()
        self.write(vals)

    def action_fail(self, error_message):
        """Mark execution as failed with error."""
        vals = {
            "state": "failed",
            "error_message": error_message,
            "completed_at": fields.Datetime.now(),
        }
        if self.started_at:
            delta = fields.Datetime.now() - self.started_at
            vals["duration_seconds"] = delta.total_seconds()
        self.write(vals)

    def action_cancel(self):
        """Cancel a queued or running execution."""
        self.write({"state": "cancelled", "completed_at": fields.Datetime.now()})
