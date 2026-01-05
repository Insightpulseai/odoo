# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectRaci(models.Model):
    _name = "ipai.project.raci"
    _description = "RACI Assignment"
    _order = "project_id, task_id, role"

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        ondelete="cascade",
        index=True,
        help="Project for project-level RACI assignment."
    )
    task_id = fields.Many2one(
        "project.task",
        string="Task",
        ondelete="cascade",
        index=True,
        help="Task for task-level RACI assignment."
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        ondelete="cascade",
        index=True
    )
    role = fields.Selection(
        [
            ("responsible", "Responsible"),
            ("accountable", "Accountable"),
            ("consulted", "Consulted"),
            ("informed", "Informed"),
        ],
        string="RACI Role",
        required=True,
        help="""
        - Responsible: Person who does the work
        - Accountable: Person ultimately answerable (only one per task/activity)
        - Consulted: Person whose input is sought (two-way communication)
        - Informed: Person kept up-to-date on progress (one-way communication)
        """
    )
    notes = fields.Text(
        string="Notes"
    )
    company_id = fields.Many2one(
        "res.company",
        compute="_compute_company_id",
        store=True,
        readonly=True
    )

    _sql_constraints = [
        (
            "unique_project_user_role",
            "UNIQUE(project_id, user_id, role)",
            "This user already has this RACI role for this project!"
        ),
        (
            "unique_task_user_role",
            "UNIQUE(task_id, user_id, role)",
            "This user already has this RACI role for this task!"
        ),
    ]

    @api.constrains("project_id", "task_id")
    def _check_project_or_task(self):
        """Ensure either project or task is set, but not both."""
        for rec in self:
            if rec.project_id and rec.task_id:
                raise ValidationError(
                    "A RACI assignment must be linked to either a project OR a task, not both."
                )
            if not rec.project_id and not rec.task_id:
                raise ValidationError(
                    "A RACI assignment must be linked to a project or a task."
                )

    @api.constrains("role", "project_id", "task_id")
    def _check_single_accountable(self):
        """Ensure only one 'Accountable' per project/task."""
        for rec in self:
            if rec.role != "accountable":
                continue

            domain = [("role", "=", "accountable"), ("id", "!=", rec.id)]
            if rec.project_id:
                domain.append(("project_id", "=", rec.project_id.id))
            else:
                domain.append(("task_id", "=", rec.task_id.id))

            existing = self.search_count(domain)
            if existing > 0:
                entity = rec.project_id.name if rec.project_id else rec.task_id.name
                raise ValidationError(
                    f"There can only be one 'Accountable' person for {entity}. "
                    "Please remove the existing assignment first."
                )

    @api.depends("project_id.company_id", "task_id.company_id")
    def _compute_company_id(self):
        for rec in self:
            if rec.project_id:
                rec.company_id = rec.project_id.company_id
            elif rec.task_id:
                rec.company_id = rec.task_id.company_id
            else:
                rec.company_id = False

    def name_get(self):
        """Custom display name."""
        result = []
        for rec in self:
            entity = rec.project_id.name if rec.project_id else rec.task_id.name
            name = f"{rec.user_id.name} - {rec.role.upper()} ({entity})"
            result.append((rec.id, name))
        return result
