# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FinancePPMLogFrame(models.Model):
    _name = 'finance.ppm.logframe'
    _description = 'Finance PPM Logical Framework'
    _order = 'level asc, code asc'
    _parent_name = 'parent_id'
    _parent_store = True

    level = fields.Selection([
        ('goal', 'Goal'),
        ('outcome', 'Outcome'),
        ('output', 'Output'),
        ('activity', 'Activity')
    ], string='Logframe Level', required=True, help='Hierarchical level in logical framework')

    code = fields.Char(
        string='Code',
        required=True,
        help='Unique code for this logframe element (e.g., GOAL-001, OUT-001)'
    )
    name = fields.Char(
        string='Name',
        required=True,
        help='Short name or title of this logframe element'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of this logframe element'
    )
    kpi_measure = fields.Char(
        string='KPI Measure',
        help='How this element will be measured (e.g., Percentage, Count, Score)'
    )
    kpi_target = fields.Char(
        string='KPI Target',
        help='Target value for this KPI (e.g., ≥90%, 100%, <5 days)'
    )
    kpi_baseline = fields.Char(
        string='KPI Baseline',
        help='Baseline value before improvement (e.g., 75%, 80%, 10 days)'
    )
    measurement_frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually')
    ], string='Measurement Frequency', help='How often this KPI is measured')

    responsible_role = fields.Char(
        string='Responsible Role',
        help='Finance role responsible for this element (e.g., Finance Director)'
    )
    parent_id = fields.Many2one(
        'finance.ppm.logframe',
        string='Parent Element',
        ondelete='cascade',
        help='Parent logframe element for hierarchical structure'
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        'finance.ppm.logframe',
        'parent_id',
        string='Child Elements'
    )

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)',
         'Logframe code must be unique!')
    ]

    @api.constrains('parent_id')
    def _check_parent_hierarchy(self):
        """Ensure parent-child relationship follows logframe hierarchy"""
        hierarchy = ['goal', 'outcome', 'output', 'activity']
        for record in self:
            if record.parent_id:
                parent_level_idx = hierarchy.index(record.parent_id.level)
                child_level_idx = hierarchy.index(record.level)
                if child_level_idx <= parent_level_idx:
                    raise ValueError(
                        f"Invalid hierarchy: {record.level} cannot be child of {record.parent_id.level}"
                    )

    def name_get(self):
        """Display name: Code - Name"""
        result = []
        for record in self:
            name = f"{record.code} - {record.name}"
            result.append((record.id, name))
        return result
