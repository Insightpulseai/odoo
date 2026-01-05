# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    # Computed flags for feature visibility
    ipai_dependencies_enabled = fields.Boolean(
        compute="_compute_ipai_flags",
        store=False,
        help="Whether dependencies feature is enabled system-wide."
    )
    ipai_milestones_enabled = fields.Boolean(
        compute="_compute_ipai_flags",
        store=False,
        help="Whether milestones feature is enabled system-wide."
    )
    ipai_budgeting_enabled = fields.Boolean(
        compute="_compute_ipai_flags",
        store=False,
        help="Whether budgeting feature is enabled system-wide."
    )
    ipai_raci_enabled = fields.Boolean(
        compute="_compute_ipai_flags",
        store=False,
        help="Whether RACI roles feature is enabled system-wide."
    )
    ipai_stage_gates_enabled = fields.Boolean(
        compute="_compute_ipai_flags",
        store=False,
        help="Whether stage gates feature is enabled system-wide."
    )
    ipai_templates_enabled = fields.Boolean(
        compute="_compute_ipai_flags",
        store=False,
        help="Whether templates feature is enabled system-wide."
    )

    # Feature-specific relational fields
    ipai_milestone_ids = fields.One2many(
        "ipai.project.milestone",
        "project_id",
        string="Milestones",
        help="Milestones associated with this project."
    )
    ipai_budget_ids = fields.One2many(
        "ipai.project.budget",
        "project_id",
        string="Budgets",
        help="Budget records for this project."
    )
    ipai_raci_ids = fields.One2many(
        "ipai.project.raci",
        "project_id",
        string="RACI Assignments",
        help="RACI role assignments for this project."
    )

    # Computed counts for smart buttons
    ipai_milestone_count = fields.Integer(
        compute="_compute_ipai_counts",
        string="Milestone Count"
    )
    ipai_budget_count = fields.Integer(
        compute="_compute_ipai_counts",
        string="Budget Count"
    )

    @api.depends_context('uid')
    def _compute_ipai_flags(self):
        """Compute feature flags from system parameters."""
        ICP = self.env["ir.config_parameter"].sudo()
        deps = ICP.get_param("ipai.project.enable_dependencies") == "True"
        ms = ICP.get_param("ipai.project.enable_milestones") == "True"
        bud = ICP.get_param("ipai.project.enable_budgeting") == "True"
        raci = ICP.get_param("ipai.project.enable_raci") == "True"
        gates = ICP.get_param("ipai.project.enable_stage_gates") == "True"
        templates = ICP.get_param("ipai.project.enable_templates") == "True"
        for rec in self:
            rec.ipai_dependencies_enabled = deps
            rec.ipai_milestones_enabled = ms
            rec.ipai_budgeting_enabled = bud
            rec.ipai_raci_enabled = raci
            rec.ipai_stage_gates_enabled = gates
            rec.ipai_templates_enabled = templates

    def _compute_ipai_counts(self):
        """Compute counts for smart buttons."""
        for rec in self:
            rec.ipai_milestone_count = len(rec.ipai_milestone_ids)
            rec.ipai_budget_count = len(rec.ipai_budget_ids)
