# -*- coding: utf-8 -*-
from odoo import models, fields, api

class OmcLogframe(models.Model):
    _name = 'omc.logframe'
    _description = 'Logical Framework Matrix'
    _order = 'sequence, id'

    name = fields.Char(string='Logframe Entry', required=True)
    level = fields.Selection([
        ('goal', 'Goal'),
        ('outcome', 'Outcome'),
        ('im1', 'Immediate Objective 1'),
        ('im2', 'Immediate Objective 2'),
        ('output', 'Output'),
        ('activity', 'Activity')
    ], string='Level', required=True, default='activity')
    indicator = fields.Text(string='Indicator')
    target = fields.Char(string='Target')
    verification = fields.Text(string='Means of Verification')
    assumptions = fields.Text(string='Assumptions')
    project_id = fields.Many2one('project.project', string='Project')
    task_ids = fields.Many2many('project.task', string='Linked Tasks')
    sequence = fields.Integer(string='Sequence', default=10)
