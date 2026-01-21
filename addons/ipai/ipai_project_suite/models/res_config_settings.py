# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Feature toggles stored in ir.config_parameter
    ipai_enable_timesheets = fields.Boolean(
        string="Enable Timesheets",
        config_parameter="ipai.project.enable_timesheets",
        help="Enable timesheet tracking and cost computation for projects and tasks.",
    )
    ipai_enable_dependencies = fields.Boolean(
        string="Enable Dependencies",
        config_parameter="ipai.project.enable_dependencies",
        help="Enable task dependencies with types (Finish-to-Start, etc.) and lag days.",
    )
    ipai_enable_milestones = fields.Boolean(
        string="Enable Milestones",
        config_parameter="ipai.project.enable_milestones",
        help="Enable project milestones with target dates and task linking.",
    )
    ipai_enable_budgeting = fields.Boolean(
        string="Enable Budgeting",
        config_parameter="ipai.project.enable_budgeting",
        help="Enable project budget management with planned and actual amounts.",
    )
    ipai_enable_raci = fields.Boolean(
        string="Enable RACI Roles",
        config_parameter="ipai.project.enable_raci",
        help="Enable RACI (Responsible/Accountable/Consulted/Informed) role assignments.",
    )
    ipai_enable_stage_gates = fields.Boolean(
        string="Enable Stage Gates",
        config_parameter="ipai.project.enable_stage_gates",
        help="Enable approval gates with required checks before advancing stages.",
    )
    ipai_enable_templates = fields.Boolean(
        string="Enable Templates",
        config_parameter="ipai.project.enable_templates",
        help="Enable project templates with pre-defined stages, tasks, and tags.",
    )
    ipai_enable_reporting_views = fields.Boolean(
        string="Enable Reporting Views",
        config_parameter="ipai.project.enable_reporting_views",
        help="Enable advanced reporting views and SQL-based KPI dashboards.",
    )
