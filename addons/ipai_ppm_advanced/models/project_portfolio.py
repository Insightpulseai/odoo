from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    portfolio_status = fields.Selection(
        [
            ('proposed', 'Proposed'),
            ('approved', 'Above Waterline (Funded)'),
            ('on_hold', 'Below Waterline (Unfunded)'),
            ('closed', 'Closed'),
        ],
        default='proposed',
        string="Portfolio Status",
        help="Portfolio governance flag inspired by Clarity PPM.",
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', readonly=True, store=True
    )
    total_baseline_cost = fields.Monetary(
        string="Baseline Budget",
        currency_field='currency_id',
        help="Optional baseline budget captured when the initiative is approved.",
    )
    total_actual_cost = fields.Monetary(
        compute="_compute_costs",
        string="Actual Cost",
        currency_field='currency_id',
        store=True,
        help="Aggregated actual cost from the linked analytic account when available.",
    )
    health_indicator = fields.Selection(
        [
            ('green', 'On Track'),
            ('amber', 'At Risk'),
            ('red', 'Critical'),
        ],
        compute="_compute_health",
        store=True,
        help="Automatically derived project health status based on schedule variance.",
    )

    @api.depends('analytic_account_id.line_ids.amount')
    def _compute_costs(self) -> None:
        for project in self:
            actual_cost = 0.0
            account = project.analytic_account_id
            if account and 'line_ids' in account._fields:
                actual_cost = -sum(account.line_ids.mapped('amount'))
            project.total_actual_cost = actual_cost

    @api.depends('task_ids.variance_duration')
    def _compute_health(self) -> None:
        for project in self:
            variances = project.task_ids.mapped('variance_duration')
            max_variance = max(variances) if variances else 0
            if max_variance > 5:
                project.health_indicator = 'red'
            elif max_variance > 0:
                project.health_indicator = 'amber'
            else:
                project.health_indicator = 'green'
