# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTemplate(models.Model):
    _name = "ipai.project.template"
    _description = "Project Template"
    _order = "sequence, name"

    name = fields.Char(string="Template Name", required=True)
    description = fields.Text(string="Description")
    sequence = fields.Integer(string="Sequence", default=10)
    stage_ids = fields.Many2many(
        "project.task.type",
        string="Stages",
        help="Stages to create for projects using this template.",
    )
    task_template_ids = fields.One2many(
        "ipai.project.template.task", "template_id", string="Task Templates"
    )
    tag_ids = fields.Many2many(
        "project.tags", string="Tags", help="Default tags for the project."
    )
    privacy_visibility = fields.Selection(
        [
            ("followers", "Invited Internal Users"),
            ("employees", "All Internal Users"),
            ("portal", "Invited Portal Users and Internal Users"),
        ],
        string="Visibility",
        default="employees",
    )
    allow_timesheets = fields.Boolean(string="Allow Timesheets", default=True)
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    def action_apply_to_project(self, project):
        """
        Apply this template to a project.

        Args:
            project: project.project record
        """
        self.ensure_one()

        # Apply stages
        if self.stage_ids:
            project.type_ids = [(6, 0, self.stage_ids.ids)]

        # Apply default settings
        vals = {}
        if self.privacy_visibility:
            vals["privacy_visibility"] = self.privacy_visibility
        if "allow_timesheets" in self.env["project.project"]._fields:
            vals["allow_timesheets"] = self.allow_timesheets
        if vals:
            project.write(vals)

        # Create tasks from task templates
        for task_tpl in self.task_template_ids:
            task_tpl._create_task(project)

        return True


class ProjectTemplateTask(models.Model):
    _name = "ipai.project.template.task"
    _description = "Project Template Task"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "ipai.project.template", string="Template", required=True, ondelete="cascade"
    )
    name = fields.Char(string="Task Name", required=True)
    description = fields.Html(string="Description")
    sequence = fields.Integer(string="Sequence", default=10)
    stage_id = fields.Many2one(
        "project.task.type",
        string="Stage",
        help="Initial stage for the task. Must be one of the template's stages.",
    )
    tag_ids = fields.Many2many("project.tags", string="Tags")
    planned_hours = fields.Float(string="Planned Hours")
    priority = fields.Selection(
        [
            ("0", "Normal"),
            ("1", "Important"),
        ],
        string="Priority",
        default="0",
    )
    parent_task_template_id = fields.Many2one(
        "ipai.project.template.task",
        string="Parent Task Template",
        domain="[('template_id', '=', template_id)]",
        help="If set, the created task will be a subtask of the task created from this template.",
    )

    def _create_task(self, project, parent_task=None):
        """
        Create a task in the project from this template.

        Args:
            project: project.project record
            parent_task: Optional parent project.task record

        Returns:
            project.task record
        """
        self.ensure_one()

        Task = self.env["project.task"]

        vals = {
            "name": self.name,
            "project_id": project.id,
            "description": self.description or "",
            "sequence": self.sequence,
            "priority": self.priority,
            "tag_ids": [(6, 0, self.tag_ids.ids)] if self.tag_ids else False,
        }

        if self.stage_id:
            vals["stage_id"] = self.stage_id.id

        if self.planned_hours:
            vals["planned_hours"] = self.planned_hours

        if parent_task:
            vals["parent_id"] = parent_task.id

        return Task.create(vals)
