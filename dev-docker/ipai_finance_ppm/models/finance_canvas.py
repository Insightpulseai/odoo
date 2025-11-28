from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json


def safe_eval(expr):
    """Safely evaluate domain expressions"""
    try:
        return eval(expr) if expr else []
    except Exception:
        return []


class FinancePPMCanvas(models.Model):
    _name = 'finance.ppm.canvas'
    _description = 'Project Canvas Dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Canvas Name', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user)

    # --- Layout Configuration ---
    layout_columns = fields.Selection([
        ('4', '4-Columns'),
        ('6', '6-Columns'),
        ('8', '8-Columns')
    ], string='Grid Layout', default='4', required=True, tracking=True)

    widget_ids = fields.One2many('finance.ppm.widget', 'canvas_id', string='Widgets')

    # --- Governance Counters ---
    widget_count = fields.Integer(compute='_compute_widget_counts', string='Total Widgets')
    table_count = fields.Integer(compute='_compute_widget_counts', string='Table Widgets')

    @api.depends('widget_ids')
    def _compute_widget_counts(self):
        for rec in self:
            rec.widget_count = len(rec.widget_ids)
            rec.table_count = len(rec.widget_ids.filtered(lambda w: w.widget_type == 'table'))

    @api.constrains('widget_ids')
    def _check_governance_limits(self):
        for rec in self:
            if len(rec.widget_ids) > 10:
                raise ValidationError(_("Governance Limit: Max 10 widgets allowed per Canvas."))

            tables = rec.widget_ids.filtered(lambda w: w.widget_type == 'table')
            if len(tables) > 7:
                raise ValidationError(_("Governance Limit: Max 7 table widgets allowed per Canvas."))


class FinancePPMWidget(models.Model):
    _name = 'finance.ppm.widget'
    _description = 'Canvas Widget'
    _order = 'sequence, id'

    canvas_id = fields.Many2one('finance.ppm.canvas', string='Canvas', ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Title', required=True)

    # --- Widget Configuration ---
    target_object = fields.Selection([
        ('finance.ppm.task', 'Tasks / Compliance'),
        ('finance.team', 'Finance Directory'),
    ], string='Target Object', default='finance.ppm.task', required=True)

    widget_type = fields.Selection([
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('tile', 'Number Tile / Progress Ring')
    ], string='Widget Category', required=True, default='chart')

    chart_type = fields.Selection([
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('line', 'Line Chart'),
        ('ring', 'Progress Ring'),
        ('number', 'Number Tile')
    ], string='Chart Type')

    # --- Data Configuration ---
    group_by_field = fields.Many2one(
        'ir.model.fields', string='Group By',
        domain="[('model', '=', target_object), ('store', '=', True)]"
    )

    measure_field = fields.Many2one(
        'ir.model.fields', string='Measure (Sum/Avg)',
        domain="[('model', '=', target_object), ('ttype', 'in', ['integer', 'float', 'monetary'])]"
    )

    operation_type = fields.Selection([
        ('count', 'Count'),
        ('sum', 'Sum'),
        ('avg', 'Average')
    ], string='Operation', default='count')

    domain_filter = fields.Char(string='Filter Domain', default='[]')

    # --- Output ---
    echarts_config = fields.Text(string='ECharts JSON', compute='_compute_echarts_json')

    def _fetch_widget_data(self):
        """
        Standardized method to fetch data.
        Useful for both ECharts generation and External Reporting (XLSX/PDF).
        Returns: (labels list, values list)
        """
        self.ensure_one()
        if not self.group_by_field:
            return [], []

        Model = self.env[self.target_object]
        domain = safe_eval(self.domain_filter) if self.domain_filter else []

        # Determine Aggregate Function
        measure = self.measure_field.name if self.measure_field else None
        fields_to_read = [self.group_by_field.name]

        if self.operation_type in ['sum', 'avg'] and measure:
            fields_to_read.append(measure)

        groups = Model.read_group(domain, fields_to_read, [self.group_by_field.name])

        labels = []
        values = []

        for g in groups:
            # 1. Resolve Label
            label_val = g[self.group_by_field.name]
            if isinstance(label_val, tuple):
                label_val = label_val[1]
            labels.append(str(label_val or 'Undefined'))

            # 2. Resolve Value
            if self.operation_type == 'count':
                val = g.get(self.group_by_field.name + '_count', 0)
            elif measure and measure in g:
                val = g[measure]
            else:
                val = 0

            values.append(val)

        return labels, values

    @api.depends('chart_type', 'group_by_field', 'measure_field', 'operation_type', 'target_object', 'domain_filter')
    def _compute_echarts_json(self):
        for rec in self:
            if rec.widget_type == 'table':
                rec.echarts_config = '{}'
                continue

            labels, values = rec._fetch_widget_data()

            # Build ECharts JSON
            config = {
                'title': {'text': rec.name, 'left': 'center'},
                'tooltip': {'trigger': 'item' if rec.chart_type == 'pie' else 'axis'},
                'toolbox': {
                    'feature': {
                        'saveAsImage': {'show': True},
                        'dataView': {'show': True, 'readOnly': True},
                    }
                }
            }

            if rec.chart_type == 'bar':
                config.update({
                    'xAxis': {'type': 'category', 'data': labels},
                    'yAxis': {'type': 'value'},
                    'series': [{'name': rec.operation_type.title(), 'type': 'bar', 'data': values}]
                })
            elif rec.chart_type == 'pie':
                pie_data = [{'name': l, 'value': v} for l, v in zip(labels, values)]
                config.update({
                    'series': [{'name': rec.name, 'type': 'pie', 'radius': '50%', 'data': pie_data}]
                })
            elif rec.chart_type == 'line':
                config.update({
                    'xAxis': {'type': 'category', 'data': labels},
                    'yAxis': {'type': 'value'},
                    'series': [{'name': rec.operation_type.title(), 'type': 'line', 'data': values}]
                })
            elif rec.chart_type == 'ring':
                # Progress ring / donut chart
                pie_data = [{'name': l, 'value': v} for l, v in zip(labels, values)]
                config.update({
                    'series': [{
                        'name': rec.name,
                        'type': 'pie',
                        'radius': ['40%', '70%'],
                        'data': pie_data,
                        'label': {'show': True, 'position': 'outside'}
                    }]
                })
            elif rec.chart_type == 'number':
                # Number tile - show total
                total = sum(values) if values else 0
                config = {
                    'title': {'text': rec.name, 'left': 'center'},
                    'series': [{
                        'type': 'gauge',
                        'data': [{'value': total, 'name': rec.name}],
                        'detail': {'formatter': '{value}'}
                    }]
                }

            rec.echarts_config = json.dumps(config, indent=2)
