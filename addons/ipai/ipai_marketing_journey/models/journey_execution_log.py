# -*- coding: utf-8 -*-
"""Marketing Journey Execution Log - audit trail for node executions."""

from odoo import fields, models


class MarketingJourneyExecutionLog(models.Model):
    """Audit log for journey node executions."""

    _name = "marketing.journey.execution.log"
    _description = "Marketing Journey Execution Log"
    _order = "execution_date desc"

    journey_id = fields.Many2one(
        "marketing.journey",
        required=True,
        ondelete="cascade",
        index=True,
    )
    participant_id = fields.Many2one(
        "marketing.journey.participant",
        required=True,
        ondelete="cascade",
        index=True,
    )
    node_id = fields.Many2one(
        "marketing.journey.node",
        required=True,
        ondelete="set null",
        index=True,
    )

    # Execution details
    execution_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
        index=True,
    )
    state = fields.Selection(
        [
            ("success", "Success"),
            ("error", "Error"),
            ("skipped", "Skipped"),
        ],
        required=True,
        index=True,
    )
    message = fields.Text()
    error_details = fields.Text()

    # Snapshot of node type at execution time
    node_type = fields.Selection(
        [
            ("entry", "Entry Point"),
            ("email", "Send Email"),
            ("sms", "Send SMS"),
            ("delay", "Wait/Delay"),
            ("branch", "Branch/Condition"),
            ("action", "Server Action"),
            ("tag", "Add/Remove Tag"),
            ("activity", "Create Activity"),
            ("exit", "Exit Journey"),
        ],
    )

    # Duration tracking (optional)
    duration_ms = fields.Integer(help="Execution duration in milliseconds")

    @classmethod
    def log_execution(cls, participant, node, result):
        """
        Create execution log entry.

        Args:
            participant: marketing.journey.participant record
            node: marketing.journey.node record
            result: dict with 'success', 'message', 'error' keys

        Returns:
            marketing.journey.execution.log record
        """
        env = participant.env
        return env["marketing.journey.execution.log"].create(
            {
                "journey_id": participant.journey_id.id,
                "participant_id": participant.id,
                "node_id": node.id,
                "node_type": node.node_type,
                "state": "success" if result.get("success") else "error",
                "message": result.get("message", ""),
                "error_details": result.get("error", ""),
            }
        )
