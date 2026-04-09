from odoo import api, fields, models, tools


class IpaiTimesheetLeaderboard(models.Model):
    _name = "ipai.timesheet.leaderboard"
    _description = "Timesheet Leaderboard"
    _auto = False
    _order = "total_hours desc"
    _rec_name = "employee_id"

    employee_id = fields.Many2one("hr.employee", readonly=True)
    department_id = fields.Many2one("hr.department", readonly=True)
    project_id = fields.Many2one("project.project", readonly=True)
    date = fields.Date(readonly=True)
    total_hours = fields.Float(
        string="Total Hours", readonly=True, group_operator="sum"
    )
    billable_hours = fields.Float(
        string="Billable Hours", readonly=True, group_operator="sum"
    )
    entry_count = fields.Integer(
        string="Entries", readonly=True, group_operator="sum"
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () AS id,
                    aal.employee_id,
                    emp.department_id,
                    aal.project_id,
                    aal.date,
                    SUM(aal.unit_amount) AS total_hours,
                    SUM(
                        CASE WHEN proj.allow_timesheets IS TRUE
                        THEN aal.unit_amount ELSE 0 END
                    ) AS billable_hours,
                    COUNT(*) AS entry_count
                FROM account_analytic_line aal
                JOIN hr_employee emp ON emp.id = aal.employee_id
                JOIN project_project proj ON proj.id = aal.project_id
                WHERE aal.project_id IS NOT NULL
                GROUP BY
                    aal.employee_id,
                    emp.department_id,
                    aal.project_id,
                    aal.date
            )
        """
            % self._table
        )
