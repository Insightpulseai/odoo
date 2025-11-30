# ipai_ppm_demo/models/ppm_dependency_node.py
from odoo import fields, models


class PpmDependencyNode(models.Model):
    _name = "ppm.dependency.node"
    _description = "PPM Dependency Node"

    name = fields.Char(required=True)
    task_id = fields.Many2one("project.task", string="Task")
    project_id = fields.Many2one("project.project", string="Project")
    dependency_type = fields.Selection(
        [
            ("finish_to_start", "Finish to Start"),
            ("start_to_start", "Start to Start"),
            ("finish_to_finish", "Finish to Finish"),
        ],
        default="finish_to_start",
    )
    critical_path = fields.Boolean(default=False)
    risk_score = fields.Float()
    assigned_resource = fields.Char()
