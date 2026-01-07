from odoo import models, fields, api
from datetime import timedelta


class CommandCenterRun(models.Model):
    _name = "ipai.command.center.run"
    _description = "Command Center Run"
    _order = "date_start desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, tracking=True)
    run_type = fields.Selection(
        [
            ("ai_query", "AI Query"),
            ("batch_job", "Batch Job"),
            ("integration", "Integration"),
            ("report", "Report"),
            ("workflow", "Workflow"),
        ],
        string="Type",
        default="batch_job",
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("running", "Running"),
            ("done", "Completed"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
        default="pending",
        required=True,
        tracking=True,
    )

    # Timing
    date_start = fields.Datetime(string="Start Time", tracking=True)
    date_end = fields.Datetime(string="End Time", tracking=True)
    duration = fields.Float(
        string="Duration (s)", compute="_compute_duration", store=True
    )

    # Execution
    result = fields.Text(string="Result (JSON)")
    error_message = fields.Text(string="Error Message")
    progress = fields.Float(string="Progress (%)", default=0.0)

    # Relations
    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.user,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    # Metrics
    records_processed = fields.Integer(string="Records Processed", default=0)
    records_failed = fields.Integer(string="Records Failed", default=0)

    @api.depends("date_start", "date_end")
    def _compute_duration(self):
        for run in self:
            if run.date_start and run.date_end:
                delta = run.date_end - run.date_start
                run.duration = delta.total_seconds()
            else:
                run.duration = 0.0

    def action_start(self):
        """Start the run."""
        self.write({
            "state": "running",
            "date_start": fields.Datetime.now(),
        })

    def action_complete(self, result=None):
        """Mark run as completed."""
        vals = {
            "state": "done",
            "date_end": fields.Datetime.now(),
            "progress": 100.0,
        }
        if result:
            vals["result"] = result
        self.write(vals)

    def action_fail(self, error_message=None):
        """Mark run as failed."""
        vals = {
            "state": "failed",
            "date_end": fields.Datetime.now(),
        }
        if error_message:
            vals["error_message"] = error_message
        self.write(vals)

    def action_cancel(self):
        """Cancel the run."""
        self.write({
            "state": "cancelled",
            "date_end": fields.Datetime.now(),
        })

    def action_retry(self):
        """Retry a failed run."""
        self.ensure_one()
        new_run = self.copy({
            "state": "pending",
            "date_start": False,
            "date_end": False,
            "error_message": False,
            "result": False,
            "progress": 0.0,
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": "ipai.command.center.run",
            "res_id": new_run.id,
            "view_mode": "form",
        }

    @api.model
    def get_dashboard_data(self):
        """Get dashboard statistics."""
        today = fields.Date.today()
        yesterday = today - timedelta(days=1)

        runs_today = self.search_count([
            ("date_start", ">=", fields.Datetime.to_string(today)),
        ])

        runs_pending = self.search_count([("state", "=", "pending")])

        runs_failed_24h = self.search_count([
            ("state", "=", "failed"),
            ("date_end", ">=", fields.Datetime.to_string(yesterday)),
        ])

        # Average duration for completed runs today
        completed_today = self.search([
            ("state", "=", "done"),
            ("date_start", ">=", fields.Datetime.to_string(today)),
        ])
        avg_duration = (
            sum(completed_today.mapped("duration")) / len(completed_today)
            if completed_today
            else 0
        )

        # By type
        by_type = {}
        for run_type, _ in self._fields["run_type"].selection:
            by_type[run_type] = self.search_count([
                ("run_type", "=", run_type),
                ("date_start", ">=", fields.Datetime.to_string(today)),
            ])

        # By state
        by_state = {}
        for state, _ in self._fields["state"].selection:
            by_state[state] = self.search_count([
                ("state", "=", state),
            ])

        return {
            "runs_today": runs_today,
            "runs_pending": runs_pending,
            "runs_failed_24h": runs_failed_24h,
            "avg_duration_ms": avg_duration * 1000,
            "by_type": by_type,
            "by_state": by_state,
        }
