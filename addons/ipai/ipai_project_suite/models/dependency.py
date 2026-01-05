# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectTaskDependency(models.Model):
    _name = "ipai.project.task.dependency"
    _description = "Task Dependency"
    _rec_name = "depends_on_task_id"

    task_id = fields.Many2one(
        "project.task",
        string="Task",
        required=True,
        ondelete="cascade",
        index=True,
        help="The task that has the dependency."
    )
    depends_on_task_id = fields.Many2one(
        "project.task",
        string="Depends On",
        required=True,
        ondelete="restrict",
        index=True,
        help="The task that must be completed first."
    )
    dependency_type = fields.Selection(
        [
            ("fs", "Finish-to-Start"),
            ("ss", "Start-to-Start"),
            ("ff", "Finish-to-Finish"),
            ("sf", "Start-to-Finish"),
        ],
        string="Type",
        default="fs",
        required=True,
        help="""
        - Finish-to-Start (FS): Task cannot start until dependency finishes
        - Start-to-Start (SS): Task cannot start until dependency starts
        - Finish-to-Finish (FF): Task cannot finish until dependency finishes
        - Start-to-Finish (SF): Task cannot finish until dependency starts
        """
    )
    lag_days = fields.Integer(
        string="Lag (days)",
        default=0,
        help="Number of days between dependency completion and task start. Negative values indicate lead time."
    )
    project_id = fields.Many2one(
        related="task_id.project_id",
        store=True,
        readonly=True
    )

    _sql_constraints = [
        (
            "unique_dependency",
            "UNIQUE(task_id, depends_on_task_id)",
            "This dependency already exists!"
        ),
    ]

    @api.constrains("task_id", "depends_on_task_id")
    def _check_no_self_dependency(self):
        """Prevent a task from depending on itself."""
        for rec in self:
            if rec.task_id == rec.depends_on_task_id:
                raise ValidationError("A task cannot depend on itself!")

    @api.constrains("task_id", "depends_on_task_id")
    def _check_no_circular_dependency(self):
        """Prevent circular dependencies."""
        for rec in self:
            visited = set()
            to_check = [rec.depends_on_task_id.id]

            while to_check:
                current = to_check.pop()
                if current == rec.task_id.id:
                    raise ValidationError(
                        f"Circular dependency detected! "
                        f"Task '{rec.task_id.name}' would create a dependency loop."
                    )
                if current in visited:
                    continue
                visited.add(current)

                # Find all tasks that the current task depends on
                deps = self.search([("task_id", "=", current)])
                to_check.extend(deps.mapped("depends_on_task_id.id"))

    def name_get(self):
        """Custom display name showing both tasks."""
        result = []
        for rec in self:
            name = f"{rec.task_id.name} → {rec.depends_on_task_id.name} ({rec.dependency_type.upper()})"
            result.append((rec.id, name))
        return result
