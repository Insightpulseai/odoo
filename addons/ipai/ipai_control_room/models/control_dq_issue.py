# -*- coding: utf-8 -*-
"""
Control Room Data Quality Issue Model
=======================================

Tracks data quality issues requiring attention.
"""

from odoo import api, fields, models


class ControlDQIssue(models.Model):
    """
    Data Quality Issue

    Represents a data quality problem identified by a rule,
    with lifecycle tracking and resolution workflow.
    """

    _name = "control.dq.issue"
    _description = "Data Quality Issue"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "opened_at DESC"

    # Identity
    name = fields.Char(
        string="Issue Name",
        compute="_compute_name",
        store=True,
    )

    # Relationships
    rule_id = fields.Many2one(
        "control.dq.rule",
        string="Rule",
        required=True,
        ondelete="restrict",
        index=True,
    )
    related_run_id = fields.Many2one(
        "control.run",
        string="Related Run",
    )
    task_id = fields.Many2one(
        "project.task",
        string="Task",
        help="Linked project task for remediation work",
    )

    # Timeline
    opened_at = fields.Datetime(
        string="Opened At",
        default=fields.Datetime.now,
        index=True,
    )
    acknowledged_at = fields.Datetime(
        string="Acknowledged At",
    )
    closed_at = fields.Datetime(
        string="Closed At",
    )
    sla_due_at = fields.Datetime(
        string="SLA Due At",
        compute="_compute_sla_due",
        store=True,
    )
    is_sla_breached = fields.Boolean(
        string="SLA Breached",
        compute="_compute_sla_status",
        store=True,
    )

    # Status
    status = fields.Selection(
        [
            ("open", "Open"),
            ("ack", "Acknowledged"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
            ("wont_fix", "Won't Fix"),
        ],
        string="Status",
        default="open",
        required=True,
        tracking=True,
        index=True,
    )

    # Assignment
    assignee_id = fields.Many2one(
        "res.users",
        string="Assignee",
        tracking=True,
    )
    team_id = fields.Many2one(
        "hr.department",
        string="Team",
    )

    # Details
    summary = fields.Char(
        string="Summary",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
    evidence_json = fields.Text(
        string="Evidence (JSON)",
        help="Metrics and data supporting the issue",
    )
    root_cause = fields.Text(
        string="Root Cause",
    )
    resolution = fields.Text(
        string="Resolution",
    )

    # Severity (inherited from rule but can be overridden)
    severity = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Severity",
        compute="_compute_severity",
        store=True,
        readonly=False,
    )

    # Related
    check_run_ids = fields.One2many(
        "control.dq.check.run",
        "issue_id",
        string="Check Runs",
    )

    @api.depends("rule_id.name", "opened_at")
    def _compute_name(self):
        for record in self:
            if record.rule_id and record.opened_at:
                ts = fields.Datetime.to_string(record.opened_at)[:10]
                record.name = f"[{ts}] {record.rule_id.name}"
            else:
                record.name = record.summary or "New Issue"

    @api.depends("rule_id.severity")
    def _compute_severity(self):
        for record in self:
            if record.rule_id:
                record.severity = record.rule_id.severity
            else:
                record.severity = "medium"

    @api.depends("opened_at", "rule_id.sla_minutes")
    def _compute_sla_due(self):
        from datetime import timedelta
        for record in self:
            if record.opened_at and record.rule_id and record.rule_id.sla_minutes:
                record.sla_due_at = record.opened_at + timedelta(minutes=record.rule_id.sla_minutes)
            else:
                record.sla_due_at = False

    @api.depends("sla_due_at", "closed_at", "status")
    def _compute_sla_status(self):
        now = fields.Datetime.now()
        for record in self:
            if not record.sla_due_at:
                record.is_sla_breached = False
            elif record.status in ("resolved", "wont_fix"):
                record.is_sla_breached = record.closed_at and record.closed_at > record.sla_due_at
            else:
                record.is_sla_breached = now > record.sla_due_at

    def action_acknowledge(self):
        """Acknowledge the issue"""
        self.write({
            "status": "ack",
            "acknowledged_at": fields.Datetime.now(),
        })

    def action_start_progress(self):
        """Mark issue as in progress"""
        self.write({"status": "in_progress"})

    def action_resolve(self):
        """Resolve the issue"""
        self.write({
            "status": "resolved",
            "closed_at": fields.Datetime.now(),
        })

    def action_wont_fix(self):
        """Mark as won't fix"""
        self.write({
            "status": "wont_fix",
            "closed_at": fields.Datetime.now(),
        })

    def action_reopen(self):
        """Reopen a closed issue"""
        self.write({
            "status": "open",
            "closed_at": False,
        })

    def action_create_task(self):
        """Create a project task for remediation"""
        self.ensure_one()
        if self.task_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "project.task",
                "res_id": self.task_id.id,
                "view_mode": "form",
                "target": "current",
            }

        Task = self.env["project.task"]
        task = Task.create({
            "name": f"DQ Issue: {self.summary}",
            "description": f"""
Data Quality Issue Remediation

Rule: {self.rule_id.name}
Severity: {self.severity}
Opened: {self.opened_at}

{self.description or ''}

Remediation Steps:
{self.rule_id.remediation or 'N/A'}
            """.strip(),
            "user_ids": [(6, 0, [self.assignee_id.id])] if self.assignee_id else False,
        })
        self.task_id = task.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "res_id": task.id,
            "view_mode": "form",
            "target": "current",
        }
