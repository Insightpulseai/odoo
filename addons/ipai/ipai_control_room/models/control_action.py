# -*- coding: utf-8 -*-
"""
Control Room Action Model
==========================

Execution records for advice/playbook actions.
"""

from odoo import api, fields, models


class ControlAction(models.Model):
    """
    Control Action

    Records the execution of an action taken in response
    to advice or playbook execution.
    """

    _name = "control.action"
    _description = "Control Action"
    _inherit = ["mail.thread"]
    _order = "create_date DESC"

    # Identity
    name = fields.Char(
        string="Action Name",
        compute="_compute_name",
        store=True,
    )

    # Relationships
    advice_id = fields.Many2one(
        "control.advice",
        string="Advice",
        ondelete="set null",
    )
    playbook_id = fields.Many2one(
        "control.playbook",
        string="Playbook",
        ondelete="set null",
    )

    # Action Type
    action_type = fields.Selection(
        [
            ("playbook_run", "Playbook Execution"),
            ("pipeline_run", "Pipeline Run"),
            ("create_task", "Create Task"),
            ("update_setting", "Update Setting"),
            ("webhook", "Webhook Call"),
            ("manual", "Manual Action"),
            ("custom", "Custom"),
        ],
        string="Action Type",
        required=True,
        default="manual",
    )

    # Configuration
    payload_json = fields.Text(
        string="Payload (JSON)",
        help="Action-specific configuration",
    )

    # State
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("running", "Running"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("canceled", "Canceled"),
        ],
        string="State",
        default="pending",
        required=True,
        tracking=True,
        index=True,
    )

    # Timing
    created_at = fields.Datetime(
        string="Created At",
        default=fields.Datetime.now,
    )
    started_at = fields.Datetime(
        string="Started At",
    )
    done_at = fields.Datetime(
        string="Done At",
    )
    duration_s = fields.Integer(
        string="Duration (seconds)",
        compute="_compute_duration",
    )

    # Result
    result_json = fields.Text(
        string="Result (JSON)",
        help="Action execution result",
    )
    error_message = fields.Text(
        string="Error Message",
    )

    # Related Records
    run_id = fields.Many2one(
        "control.run",
        string="Triggered Run",
        help="Pipeline run triggered by this action",
    )
    task_id = fields.Many2one(
        "project.task",
        string="Created Task",
        help="Task created by this action",
    )

    # Ownership
    user_id = fields.Many2one(
        "res.users",
        string="Executed By",
        default=lambda self: self.env.user,
    )

    @api.depends("action_type", "playbook_id", "advice_id", "create_date")
    def _compute_name(self):
        for record in self:
            parts = []
            if record.action_type:
                parts.append(dict(self._fields["action_type"].selection).get(record.action_type, ""))
            if record.playbook_id:
                parts.append(f"[{record.playbook_id.name}]")
            elif record.advice_id:
                parts.append(f"[{record.advice_id.title}]")
            if record.create_date:
                parts.append(f"@ {fields.Datetime.to_string(record.create_date)[:16]}")
            record.name = " ".join(parts) if parts else "New Action"

    @api.depends("started_at", "done_at")
    def _compute_duration(self):
        for record in self:
            if record.started_at and record.done_at:
                delta = record.done_at - record.started_at
                record.duration_s = int(delta.total_seconds())
            else:
                record.duration_s = 0

    def action_start(self):
        """Start the action execution"""
        self.write({
            "state": "running",
            "started_at": fields.Datetime.now(),
        })

    def action_complete(self, result=None):
        """Complete the action"""
        vals = {
            "state": "completed",
            "done_at": fields.Datetime.now(),
        }
        if result:
            vals["result_json"] = result
        self.write(vals)

    def action_fail(self, error_message=None):
        """Mark action as failed"""
        self.write({
            "state": "failed",
            "done_at": fields.Datetime.now(),
            "error_message": error_message,
        })

    def action_cancel(self):
        """Cancel the action"""
        self.write({
            "state": "canceled",
            "done_at": fields.Datetime.now(),
        })

    def action_execute(self):
        """Execute the action based on its type"""
        self.ensure_one()
        self.action_start()

        try:
            if self.action_type == "pipeline_run" and self.playbook_id and self.playbook_id.automation_pipeline_id:
                result = self.playbook_id.automation_pipeline_id.action_trigger_run()
                if result and result.get("res_id"):
                    self.run_id = result["res_id"]
                self.action_complete()
            elif self.action_type == "create_task":
                Task = self.env["project.task"]
                task = Task.create({
                    "name": f"Action: {self.name}",
                    "description": self.payload_json or "",
                })
                self.task_id = task.id
                self.action_complete()
            else:
                # Placeholder for other action types
                self.action_complete()
        except Exception as e:
            self.action_fail(str(e))
            raise

        return True
