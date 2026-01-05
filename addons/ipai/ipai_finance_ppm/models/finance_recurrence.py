# -*- coding: utf-8 -*-
"""
Finance Recurrence Rule Model.

Defines recurring patterns for automated finance task generation.
Used by the month-end close and BIR compliance workflows.
"""
from odoo import fields, models


class FinanceRecurrenceRule(models.Model):
    """
    Recurrence Rule for Finance Tasks.

    Defines patterns like:
    - Monthly on day 5
    - Quarterly on last business day
    - Annual on specific BIR deadline
    """

    _name = "finance.recurrence.rule"
    _description = "Finance Recurrence Rule"
    _order = "name"

    name = fields.Char(
        string="Rule Name",
        required=True,
        help="Descriptive name for the recurrence pattern",
    )

    recurrence_type = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
            ("bir_linked", "BIR Deadline Linked"),
        ],
        string="Recurrence Type",
        required=True,
        default="monthly",
    )

    day_of_month = fields.Integer(
        string="Day of Month",
        default=1,
        help="Day of month for fixed-date recurrence (1-31). "
        "Use 0 for last day of month.",
    )

    offset_workdays = fields.Integer(
        string="Workday Offset",
        default=0,
        help="Number of workdays before (-) or after (+) the base date",
    )

    bir_form_id = fields.Many2one(
        "ipai.finance.bir_schedule",
        string="BIR Form",
        help="Link to BIR form for deadline-linked recurrence",
    )

    active = fields.Boolean(default=True)

    task_ids = fields.One2many(
        "project.task",
        "recurrence_rule_id",
        string="Linked Tasks",
    )

    task_count = fields.Integer(
        string="Task Count",
        compute="_compute_task_count",
    )

    def _compute_task_count(self):
        for rule in self:
            rule.task_count = len(rule.task_ids)
