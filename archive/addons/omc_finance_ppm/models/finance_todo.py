# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FinanceTodo(models.Model):
    _name = 'finance.todo'
    _description = 'Finance To-Do Item'
    _order = 'sequence, id'

    name = fields.Char(string='To-Do', required=True)
    is_done = fields.Boolean(string='Done', default=False)
    assignee_id = fields.Many2one('res.users', string='Assigned To')
    task_id = fields.Many2one('project.task', string='Related Task')
    sequence = fields.Integer(string='Sequence', default=10)
