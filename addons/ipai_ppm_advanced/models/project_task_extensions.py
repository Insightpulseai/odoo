import datetime

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'
    baseline_date_start = fields.Datetime(
        string="Baseline Start",
        help="Snapshot of the planned start date when the baseline was set.",
    )
    baseline_date_end = fields.Datetime(
        string="Baseline Finish",
        help="Snapshot of the planned finish date when the baseline was set.",
    )
    variance_duration = fields.Float(
        string="Variance (Days)",
        compute="_compute_variance",
        store=True,
        help="Difference in days between the current deadline and the baseline finish date.",
    )
    constraint_type = fields.Selection(
        [
            ('asap', 'As Soon As Possible'),
            ('alap', 'As Late As Possible'),
            ('fnet', 'Finish No Earlier Than'),
            ('snet', 'Start No Earlier Than'),
        ],
        default='asap',
        string="Constraint Type",
        help="Scheduling constraint inspired by Microsoft Project.",
    )
    constraint_date = fields.Datetime(
        string="Constraint Date",
        help="Reference date used when applying the selected constraint.",
    )

    @api.depends('date_deadline', 'baseline_date_end')
    def _compute_variance(self) -> None:
        for task in self:
            baseline_end = task.baseline_date_end
            deadline = task.date_deadline
            if baseline_end and deadline:
                baseline_date = fields.Datetime.to_datetime(baseline_end).date()
                task.variance_duration = float((deadline - baseline_date).days)
            else:
                task.variance_duration = 0.0

    def _get_deadline_datetime(self) -> datetime.datetime | bool:
        self.ensure_one()
        if self.date_deadline:
            return datetime.datetime.combine(self.date_deadline, datetime.time.min)
        return False

    def action_set_baseline(self) -> None:
        """Freeze current planned dates into baseline fields."""
        for task in self:
            baseline_start = task.planned_date_begin or task.date_assign or fields.Datetime.now()
            baseline_end = task.planned_date_end or task._get_deadline_datetime() or fields.Datetime.now()
            task.write(
                {
                    'baseline_date_start': baseline_start,
                    'baseline_date_end': baseline_end,
                }
            )
