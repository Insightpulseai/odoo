# -*- coding: utf-8 -*-
"""
Control Room Schedule Model
============================

Schedule definitions for automated pipeline execution.
"""

from odoo import api, fields, models


class ControlSchedule(models.Model):
    """
    Control Schedule

    Defines when pipelines should be triggered automatically.
    Can link to native ir.cron or use custom cron expressions.
    """

    _name = "control.schedule"
    _description = "Control Schedule"
    _order = "name"

    # Identity
    name = fields.Char(
        string="Schedule Name",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # Schedule Definition
    schedule_type = fields.Selection(
        [
            ("cron", "Cron Expression"),
            ("interval", "Interval"),
            ("ir_cron", "Odoo Scheduled Action"),
        ],
        string="Schedule Type",
        default="cron",
        required=True,
    )
    cron_expr = fields.Char(
        string="Cron Expression",
        help="Standard cron expression (minute hour day month weekday)",
    )
    interval_number = fields.Integer(
        string="Interval",
        default=1,
    )
    interval_type = fields.Selection(
        [
            ("minutes", "Minutes"),
            ("hours", "Hours"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
        ],
        string="Interval Type",
        default="hours",
    )
    ir_cron_id = fields.Many2one(
        "ir.cron",
        string="Scheduled Action",
        help="Link to native Odoo scheduled action",
    )

    # Timezone
    timezone = fields.Selection(
        "_get_timezone_selection",
        string="Timezone",
        default="UTC",
    )

    # Next Run
    next_run_at = fields.Datetime(
        string="Next Run At",
        compute="_compute_next_run",
        store=True,
    )
    last_run_at = fields.Datetime(
        string="Last Run At",
    )

    # Related Pipelines
    pipeline_ids = fields.One2many(
        "control.pipeline",
        "schedule_id",
        string="Pipelines",
    )
    pipeline_count = fields.Integer(
        string="Pipeline Count",
        compute="_compute_pipeline_count",
    )

    # Description
    description = fields.Text(
        string="Description",
    )

    @api.model
    def _get_timezone_selection(self):
        """Return list of common timezones"""
        return [
            ("UTC", "UTC"),
            ("Asia/Manila", "Asia/Manila (PHT)"),
            ("Asia/Singapore", "Asia/Singapore (SGT)"),
            ("America/New_York", "America/New_York (EST)"),
            ("America/Los_Angeles", "America/Los_Angeles (PST)"),
            ("Europe/London", "Europe/London (GMT)"),
            ("Europe/Paris", "Europe/Paris (CET)"),
            ("Asia/Tokyo", "Asia/Tokyo (JST)"),
            ("Australia/Sydney", "Australia/Sydney (AEDT)"),
        ]

    @api.depends("schedule_type", "cron_expr", "interval_number", "interval_type")
    def _compute_next_run(self):
        """Compute next run timestamp based on schedule"""
        # Placeholder - actual implementation would parse cron/interval
        for record in self:
            record.next_run_at = False

    @api.depends("pipeline_ids")
    def _compute_pipeline_count(self):
        for record in self:
            record.pipeline_count = len(record.pipeline_ids)
