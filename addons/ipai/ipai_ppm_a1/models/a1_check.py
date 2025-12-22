# -*- coding: utf-8 -*-
"""
A1 Check (STC Scenario)

Represents validation/verification scenarios that can be linked to tasks.
These become approval gates in the close orchestration module.
"""
from odoo import api, fields, models


class A1Check(models.Model):
    """
    Check/Scenario definition for validation rules.

    STCs (Standard Test Cases) define what must be verified before task completion.
    """

    _name = "a1.check"
    _description = "A1 Check / STC Scenario"
    _order = "sequence, code"

    _sql_constraints = [
        (
            "code_uniq",
            "unique(code, company_id)",
            "Check code must be unique per company.",
        ),
    ]

    # Core fields
    code = fields.Char(
        string="Code",
        required=True,
        index=True,
        help="Unique identifier like 'STC_001', 'VAL_RECON'",
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)

    # Classification
    check_type = fields.Selection(
        [
            ("manual", "Manual Verification"),
            ("automated", "Automated Check"),
            ("approval", "Approval Gate"),
            ("reconciliation", "Reconciliation"),
        ],
        string="Type",
        default="manual",
        required=True,
    )

    severity = fields.Selection(
        [
            ("info", "Informational"),
            ("warning", "Warning"),
            ("blocker", "Blocker"),
        ],
        string="Severity",
        default="warning",
        required=True,
    )

    # Linked templates (many2many - a check can apply to multiple templates)
    template_ids = fields.Many2many(
        "a1.template",
        "a1_template_check_rel",
        "check_id",
        "template_id",
        string="Applicable Templates",
    )

    # Criteria
    description = fields.Html(
        string="Description",
        help="What this check verifies",
    )
    pass_criteria = fields.Text(
        string="Pass Criteria",
        help="Conditions that must be met to pass",
    )
    fail_action = fields.Text(
        string="Failure Action",
        help="What to do if check fails",
    )

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # Bridge to close orchestration
    close_gate_template_id = fields.Many2one(
        "close.approval.gate.template",
        string="Close Gate Template",
        help="Linked gate template in Close Orchestration module",
    )


class A1CheckResult(models.Model):
    """
    Result of a check execution for a specific task.
    """

    _name = "a1.check.result"
    _description = "A1 Check Result"
    _order = "create_date desc"

    check_id = fields.Many2one(
        "a1.check",
        string="Check",
        required=True,
        ondelete="cascade",
    )
    task_id = fields.Many2one(
        "a1.task",
        string="Task",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # Result
    result = fields.Selection(
        [
            ("pending", "Pending"),
            ("pass", "Pass"),
            ("fail", "Fail"),
            ("skip", "Skipped"),
        ],
        string="Result",
        default="pending",
        required=True,
    )

    result_notes = fields.Text(string="Result Notes")

    # Execution
    executed_by = fields.Many2one("res.users", string="Executed By")
    executed_date = fields.Datetime(string="Executed At")

    # Evidence
    evidence = fields.Html(string="Evidence")
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Attachments",
    )
