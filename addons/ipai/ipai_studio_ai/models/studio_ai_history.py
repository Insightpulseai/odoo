# -*- coding: utf-8 -*-
"""
IPAI Studio AI - Command History Model
======================================

Tracks all Studio AI commands and their results for analytics and improvement.
"""

from odoo import _, api, fields, models


class StudioAIHistory(models.Model):
    """Track Studio AI command history."""

    _name = "ipai.studio.ai.history"
    _description = "Studio AI Command History"
    _order = "create_date desc"
    _rec_name = "command"

    command = fields.Text(
        string="Command",
        required=True,
        help="The natural language command that was processed",
    )
    command_type = fields.Selection(
        [
            ("field", "Field Creation"),
            ("view", "View Modification"),
            ("automation", "Automation"),
            ("report", "Report"),
            ("unknown", "Unknown"),
        ],
        string="Type",
        default="unknown",
    )

    model_id = fields.Many2one(
        "ir.model",
        string="Target Model",
        ondelete="set null",
    )
    model_name = fields.Char(
        string="Model Name",
        related="model_id.model",
        store=True,
    )

    confidence = fields.Float(
        string="Confidence",
        digits=(3, 2),
        help="AI confidence score for the command interpretation",
    )

    analysis = fields.Text(
        string="Analysis",
        help="JSON representation of the command analysis",
    )

    result = fields.Selection(
        [
            ("pending", "Pending"),
            ("executed", "Executed"),
            ("cancelled", "Cancelled"),
            ("failed", "Failed"),
        ],
        string="Result",
        default="pending",
    )

    result_message = fields.Text(
        string="Result Message",
        help="Message or error from execution",
    )

    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.user,
        required=True,
    )

    # Created artifacts
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Created Field",
        ondelete="set null",
    )
    automation_id = fields.Many2one(
        "base.automation",
        string="Created Automation",
        ondelete="set null",
    )

    # Feedback
    feedback_score = fields.Selection(
        [
            ("-1", "Not Helpful"),
            ("0", "Neutral"),
            ("1", "Helpful"),
        ],
        string="Feedback",
    )
    feedback_comment = fields.Text(string="Feedback Comment")

    @api.model
    def log_command(self, command: str, result: dict) -> "StudioAIHistory":
        """Log a processed command."""
        import json

        vals = {
            "command": command,
            "command_type": result.get("type", "unknown"),
            "confidence": result.get("confidence", 0.0),
            "analysis": json.dumps(result.get("analysis", {})),
            "result": "pending",
        }

        # Set model if detected
        if result.get("analysis", {}).get("model_id"):
            vals["model_id"] = result["analysis"]["model_id"]

        return self.create(vals)

    def mark_executed(
        self, message: str = "", field_id: int = None, automation_id: int = None
    ):
        """Mark command as executed."""
        vals = {
            "result": "executed",
            "result_message": message,
        }
        if field_id:
            vals["field_id"] = field_id
        if automation_id:
            vals["automation_id"] = automation_id
        self.write(vals)

    def mark_failed(self, error: str):
        """Mark command as failed."""
        self.write(
            {
                "result": "failed",
                "result_message": error,
            }
        )

    def mark_cancelled(self):
        """Mark command as cancelled."""
        self.write({"result": "cancelled"})


class StudioAIStats(models.Model):
    """Analytics for Studio AI usage."""

    _name = "ipai.studio.ai.stats"
    _description = "Studio AI Statistics"
    _auto = False
    _order = "date desc"

    date = fields.Date(string="Date", readonly=True)
    command_type = fields.Selection(
        [
            ("field", "Field Creation"),
            ("view", "View Modification"),
            ("automation", "Automation"),
            ("report", "Report"),
            ("unknown", "Unknown"),
        ],
        string="Type",
        readonly=True,
    )
    total_commands = fields.Integer(string="Total Commands", readonly=True)
    executed_commands = fields.Integer(string="Executed", readonly=True)
    failed_commands = fields.Integer(string="Failed", readonly=True)
    avg_confidence = fields.Float(string="Avg Confidence", readonly=True)

    def init(self):
        """Create the analytics view."""
        self.env.cr.execute(
            """
            DROP VIEW IF EXISTS ipai_studio_ai_stats;
            CREATE OR REPLACE VIEW ipai_studio_ai_stats AS (
                SELECT
                    row_number() OVER () as id,
                    DATE(create_date) as date,
                    command_type,
                    COUNT(*) as total_commands,
                    COUNT(CASE WHEN result = 'executed' THEN 1 END) as executed_commands,
                    COUNT(CASE WHEN result = 'failed' THEN 1 END) as failed_commands,
                    AVG(confidence) as avg_confidence
                FROM ipai_studio_ai_history
                GROUP BY DATE(create_date), command_type
            )
        """
        )
