# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_phase = fields.Boolean(string='Is Phase', default=False,
                              help='Mark this task as a phase parent for PPM hierarchy')
    todo_ids = fields.One2many('finance.todo', 'task_id', string='To-Do Items')
    logframe_ids = fields.Many2many('omc.logframe', string='Linked Logframe Entries')
