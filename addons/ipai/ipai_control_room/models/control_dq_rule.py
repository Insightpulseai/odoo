# -*- coding: utf-8 -*-
"""
Control Room Data Quality Rule Model
=====================================

Defines data quality rules for validation and monitoring.
"""

from odoo import api, fields, models


class ControlDQRule(models.Model):
    """
    Data Quality Rule

    Defines a data quality check that can be run against
    tables, models, datasets, or endpoints.
    """

    _name = "control.dq.rule"
    _description = "Data Quality Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "severity DESC, name"

    # Identity
    name = fields.Char(
        string="Rule Name",
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string="Rule Code",
        index=True,
        help="Unique identifier for the rule",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # Ownership
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=True,
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
        tracking=True,
    )

    # Target Scope
    scope = fields.Selection(
        [
            ("table", "Database Table"),
            ("model", "Odoo Model"),
            ("dataset", "External Dataset"),
            ("endpoint", "API Endpoint"),
        ],
        string="Scope",
        required=True,
        default="model",
    )
    target = fields.Char(
        string="Target",
        required=True,
        help="Model name, table name, dataset ID, or endpoint URL",
    )
    target_field = fields.Char(
        string="Target Field",
        help="Specific field/column to validate",
    )

    # Rule Type
    rule_type = fields.Selection(
        [
            ("not_null", "Not Null"),
            ("unique", "Unique"),
            ("range", "Value Range"),
            ("enum", "Enum / Allowed Values"),
            ("regex", "Regex Pattern"),
            ("schema", "Schema Validation"),
            ("drift", "Data Drift"),
            ("freshness", "Data Freshness"),
            ("row_count", "Row Count"),
            ("custom_sql", "Custom SQL"),
            ("custom_python", "Custom Python"),
        ],
        string="Rule Type",
        required=True,
        default="not_null",
    )

    # Severity
    severity = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Severity",
        default="medium",
        required=True,
        tracking=True,
    )

    # Configuration
    params_json = fields.Text(
        string="Parameters (JSON)",
        help="Rule-specific configuration",
        default="{}",
    )
    threshold = fields.Float(
        string="Threshold",
        help="Numeric threshold for range/count rules",
    )
    allowed_values = fields.Text(
        string="Allowed Values",
        help="Comma-separated list of allowed values for enum rules",
    )
    regex_pattern = fields.Char(
        string="Regex Pattern",
        help="Regular expression for regex rules",
    )
    custom_sql = fields.Text(
        string="Custom SQL",
        help="SQL query that should return 0 rows for pass",
    )

    # SLA
    sla_minutes = fields.Integer(
        string="SLA (minutes)",
        help="Maximum time to resolve issues from this rule",
    )

    # Scheduling
    check_frequency = fields.Selection(
        [
            ("manual", "Manual Only"),
            ("hourly", "Hourly"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
        ],
        string="Check Frequency",
        default="daily",
    )
    last_check_at = fields.Datetime(
        string="Last Check At",
    )
    last_check_status = fields.Selection(
        [
            ("pass", "Pass"),
            ("fail", "Fail"),
            ("error", "Error"),
        ],
        string="Last Check Status",
    )

    # Related
    check_run_ids = fields.One2many(
        "control.dq.check.run",
        "rule_id",
        string="Check Runs",
    )
    issue_ids = fields.One2many(
        "control.dq.issue",
        "rule_id",
        string="Issues",
    )
    open_issue_count = fields.Integer(
        string="Open Issues",
        compute="_compute_open_issue_count",
    )

    # Description
    description = fields.Text(
        string="Description",
    )
    remediation = fields.Text(
        string="Remediation Steps",
        help="Instructions for fixing issues from this rule",
    )

    _sql_constraints = [
        (
            "code_company_uniq",
            "UNIQUE(code, company_id)",
            "Rule code must be unique per company",
        )
    ]

    @api.depends("issue_ids.status")
    def _compute_open_issue_count(self):
        for record in self:
            record.open_issue_count = len(
                record.issue_ids.filtered(lambda i: i.status in ("open", "ack", "in_progress"))
            )

    def action_run_check(self):
        """Trigger a check run for this rule"""
        self.ensure_one()
        CheckRun = self.env["control.dq.check.run"]
        check = CheckRun.create({
            "rule_id": self.id,
            "state": "pass",  # Placeholder - actual check logic would determine
        })
        self.write({
            "last_check_at": fields.Datetime.now(),
            "last_check_status": check.state,
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": "control.dq.check.run",
            "res_id": check.id,
            "view_mode": "form",
            "target": "current",
        }
