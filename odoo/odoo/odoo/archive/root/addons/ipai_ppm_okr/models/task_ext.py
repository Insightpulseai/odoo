from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    ppm_epic_id = fields.Many2one("ppm.epic", ondelete="set null", index=True)
    okr_initiative_ids = fields.One2many("okr.initiative", "task_id")
