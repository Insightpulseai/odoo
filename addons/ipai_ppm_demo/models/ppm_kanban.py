# ipai_ppm_demo/models/ppm_kanban.py
from odoo import fields, models


class PpmKanbanColumn(models.Model):
    _name = "ppm.kanban.column"
    _description = "PPM Demo Kanban Column"
    _order = "sequence, id"

    name = fields.Char(required=True)
    code = fields.Char()
    sequence = fields.Integer(default=10)
    card_ids = fields.One2many("ppm.kanban.card", "column_id", string="Cards")


class PpmKanbanCard(models.Model):
    _name = "ppm.kanban.card"
    _description = "PPM Demo Kanban Card"
    _order = "column_id, sequence, id"

    name = fields.Char(required=True)
    column_id = fields.Many2one("ppm.kanban.column", required=True)
    project_id = fields.Many2one("project.project", string="Project")
    owner = fields.Char()
    progress_percent = fields.Integer()
    risk_reason = fields.Char()
    sequence = fields.Integer(default=10)
