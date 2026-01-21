# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    # Computed flags for feature visibility
    ipai_dependencies_enabled = fields.Boolean(
        compute="_compute_ipai_flags",
        store=False,
        help="Whether dependencies feature is enabled system-wide.",
    )
    ipai_milestones_enabled = fields.Boolean(
        compute="_compute_ipai_flags",
        store=False,
        help="Whether milestones feature is enabled system-wide.",
    )
    ipai_budgeting_enabled = fields.Boolean(
        compute="_compute_ipai_flags",
        store=False,
        help="Whether budgeting feature is enabled system-wide.",
    )
    ipai_raci_enabled = fields.Boolean(
        compute="_compute_ipai_flags",
        store=False,
        help="Whether RACI roles feature is enabled system-wide.",
    )
    ipai_stage_gates_enabled = fields.Boolean(
        compute="_compute_ipai_flags",
        store=False,
        help="Whether stage gates feature is enabled system-wide.",
    )

    # Feature-specific relational fields
    ipai_dependency_ids = fields.One2many(
        "ipai.project.task.dependency",
        "task_id",
        string="Dependencies",
        help="Tasks that this task depends on.",
    )
    ipai_dependent_ids = fields.One2many(
        "ipai.project.task.dependency",
        "depends_on_task_id",
        string="Dependents",
        help="Tasks that depend on this task.",
    )
    ipai_milestone_id = fields.Many2one(
        "ipai.project.milestone",
        string="Milestone",
        help="Milestone this task contributes to.",
    )
    ipai_raci_ids = fields.One2many(
        "ipai.project.raci",
        "task_id",
        string="RACI Assignments",
        help="RACI role assignments for this task.",
    )

    # Computed fields
    ipai_dependency_count = fields.Integer(
        compute="_compute_ipai_dependency_count", string="Dependency Count"
    )

    @api.depends_context("uid")
    def _compute_ipai_flags(self):
        """Compute feature flags from system parameters."""
        ICP = self.env["ir.config_parameter"].sudo()
        deps = ICP.get_param("ipai.project.enable_dependencies") == "True"
        ms = ICP.get_param("ipai.project.enable_milestones") == "True"
        bud = ICP.get_param("ipai.project.enable_budgeting") == "True"
        raci = ICP.get_param("ipai.project.enable_raci") == "True"
        gates = ICP.get_param("ipai.project.enable_stage_gates") == "True"
        for rec in self:
            rec.ipai_dependencies_enabled = deps
            rec.ipai_milestones_enabled = ms
            rec.ipai_budgeting_enabled = bud
            rec.ipai_raci_enabled = raci
            rec.ipai_stage_gates_enabled = gates

    def _compute_ipai_dependency_count(self):
        """Compute the number of dependencies for each task."""
        for rec in self:
            rec.ipai_dependency_count = len(rec.ipai_dependency_ids)
