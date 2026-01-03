# -*- coding: utf-8 -*-
"""Extend project.task with deadline offset field."""
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    ipai_deadline_offset_workdays = fields.Integer(
        string="Deadline Offset (Workdays)",
        default=0,
        help="Workdays BEFORE month-end. Uses company working calendar + holidays.",
    )
