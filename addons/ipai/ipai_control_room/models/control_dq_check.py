# -*- coding: utf-8 -*-
"""
Control Room Data Quality Check Run Model
==========================================

Records individual executions of data quality rules.
"""

from odoo import api, fields, models


class ControlDQCheckRun(models.Model):
    """
    Data Quality Check Run

    Records the execution of a data quality rule,
    including metrics and sample data.
    """

    _name = "control.dq.check.run"
    _description = "Data Quality Check Run"
    _order = "checked_at DESC"

    # Relationships
    rule_id = fields.Many2one(
        "control.dq.rule",
        string="Rule",
        required=True,
        ondelete="cascade",
        index=True,
    )
    run_id = fields.Many2one(
        "control.run",
        string="Pipeline Run",
        help="Optional link to pipeline run that triggered this check",
        index=True,
    )

    # Timing
    checked_at = fields.Datetime(
        string="Checked At",
        default=fields.Datetime.now,
        index=True,
    )
    duration_ms = fields.Integer(
        string="Duration (ms)",
    )

    # Result
    state = fields.Selection(
        [
            ("pass", "Pass"),
            ("fail", "Fail"),
            ("error", "Error"),
        ],
        string="State",
        required=True,
        index=True,
    )
    error_message = fields.Text(
        string="Error Message",
        help="Error details if check errored",
    )

    # Metrics
    metrics_json = fields.Text(
        string="Metrics (JSON)",
        help="Structured metrics from the check (row_count, null_count, etc.)",
    )
    row_count = fields.Integer(
        string="Row Count",
    )
    failure_count = fields.Integer(
        string="Failure Count",
        help="Number of rows/records that failed the check",
    )
    failure_rate = fields.Float(
        string="Failure Rate (%)",
        compute="_compute_failure_rate",
    )

    # Sample Data
    sample_artifact_id = fields.Many2one(
        "control.artifact",
        string="Sample Artifact",
        help="Optional sample of failing records",
    )
    sample_json = fields.Text(
        string="Sample Data (JSON)",
        help="Sample of failing records (for small datasets)",
    )

    # Related
    issue_id = fields.Many2one(
        "control.dq.issue",
        string="Created Issue",
        help="Issue created from this failed check",
    )

    @api.depends("row_count", "failure_count")
    def _compute_failure_rate(self):
        for record in self:
            if record.row_count and record.row_count > 0:
                record.failure_rate = (record.failure_count / record.row_count) * 100
            else:
                record.failure_rate = 0.0

    def action_create_issue(self):
        """Create a DQ issue from this failed check"""
        self.ensure_one()
        if self.state != "fail":
            return False

        Issue = self.env["control.dq.issue"]
        issue = Issue.create(
            {
                "rule_id": self.rule_id.id,
                "related_run_id": self.run_id.id if self.run_id else False,
                "summary": f"DQ Check Failed: {self.rule_id.name}",
                "evidence_json": self.metrics_json,
            }
        )
        self.issue_id = issue.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "control.dq.issue",
            "res_id": issue.id,
            "view_mode": "form",
            "target": "current",
        }
