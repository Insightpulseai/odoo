from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class BirFilingDeadline(models.Model):
    """BIR Filing Deadline Calendar"""

    _name = "bir.filing.deadline"
    _description = "BIR Filing Deadline"
    _order = "deadline_date"

    name = fields.Char(string="Description", required=True)
    form_type = fields.Selection(
        [
            ("2550M", "2550M - Monthly VAT"),
            ("2550Q", "2550Q - Quarterly VAT"),
            ("1600", "1600 - VAT/Percentage WHT"),
            ("1601C", "1601-C - Compensation WHT"),
            ("1601E", "1601-E - Expanded WHT"),
            ("1601F", "1601-F - Final WHT"),
            ("1604CF", "1604-CF - Annual Alphalist"),
            ("1700", "1700 - Annual Income Tax"),
            ("1701", "1701 - Annual Income Tax"),
            ("1701Q", "1701Q - Quarterly Income Tax"),
            ("1702RT", "1702-RT - Corporate Tax"),
            ("2551M", "2551M - Monthly Percentage Tax"),
            ("2200A", "2200A - Excise (Alcohol)"),
            ("2200T", "2200T - Excise (Tobacco)"),
        ],
        string="Form Type",
        required=True,
    )
    period_month = fields.Integer(string="Period Month", help="1-12")
    period_year = fields.Integer(string="Period Year")
    deadline_date = fields.Date(string="Filing Deadline", required=True)
    reminder_date = fields.Date(
        string="Reminder Date",
        compute="_compute_reminder_date",
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    return_id = fields.Many2one(
        "bir.tax.return",
        string="Linked Return",
    )
    state = fields.Selection(
        [
            ("upcoming", "Upcoming"),
            ("due_soon", "Due Soon (5 days)"),
            ("overdue", "Overdue"),
            ("filed", "Filed"),
        ],
        string="Status",
        compute="_compute_state",
        store=True,
    )

    @api.depends("deadline_date")
    def _compute_reminder_date(self):
        for rec in self:
            if rec.deadline_date:
                rec.reminder_date = rec.deadline_date - relativedelta(days=5)
            else:
                rec.reminder_date = False

    @api.depends("deadline_date", "return_id.state")
    def _compute_state(self):
        today = fields.Date.today()
        for rec in self:
            if rec.return_id and rec.return_id.state in ("filed", "confirmed"):
                rec.state = "filed"
            elif rec.deadline_date < today:
                rec.state = "overdue"
            elif (rec.deadline_date - today).days <= 5:
                rec.state = "due_soon"
            else:
                rec.state = "upcoming"

    @api.model
    def _cron_generate_deadlines(self):
        """Generate filing deadlines for the current year"""
        today = fields.Date.today()
        current_year = today.year
        companies = self.env["res.company"].search([])

        monthly_forms = ["2550M", "1601C", "1601E", "2551M"]
        quarterly_forms = ["2550Q", "1701Q"]

        for company in companies:
            # Monthly deadlines (20th of following month)
            for month in range(1, 13):
                period_end = fields.Date.today().replace(
                    year=current_year, month=month, day=1
                )
                period_end = period_end + relativedelta(months=1, days=-1)
                deadline = period_end + relativedelta(months=1, day=20)

                for form in monthly_forms:
                    existing = self.search(
                        [
                            ("company_id", "=", company.id),
                            ("form_type", "=", form),
                            ("period_month", "=", month),
                            ("period_year", "=", current_year),
                        ],
                        limit=1,
                    )
                    if not existing:
                        self.create(
                            {
                                "name": f"{form} - {month:02d}/{current_year}",
                                "form_type": form,
                                "period_month": month,
                                "period_year": current_year,
                                "deadline_date": deadline,
                                "company_id": company.id,
                            }
                        )

            # Quarterly deadlines (25th of month following quarter)
            for quarter in [3, 6, 9, 12]:
                period_end = fields.Date.today().replace(
                    year=current_year, month=quarter, day=1
                )
                period_end = period_end + relativedelta(months=1, days=-1)
                deadline = period_end + relativedelta(months=1, day=25)

                for form in quarterly_forms:
                    existing = self.search(
                        [
                            ("company_id", "=", company.id),
                            ("form_type", "=", form),
                            ("period_month", "=", quarter),
                            ("period_year", "=", current_year),
                        ],
                        limit=1,
                    )
                    if not existing:
                        self.create(
                            {
                                "name": f"{form} - Q{quarter//3}/{current_year}",
                                "form_type": form,
                                "period_month": quarter,
                                "period_year": current_year,
                                "deadline_date": deadline,
                                "company_id": company.id,
                            }
                        )

            # Annual deadlines (April 15)
            annual_deadline = fields.Date.today().replace(
                year=current_year + 1, month=4, day=15
            )
            annual_forms = ["1604CF", "1700", "1701", "1702RT"]
            for form in annual_forms:
                existing = self.search(
                    [
                        ("company_id", "=", company.id),
                        ("form_type", "=", form),
                        ("period_year", "=", current_year),
                    ],
                    limit=1,
                )
                if not existing:
                    self.create(
                        {
                            "name": f"{form} - {current_year}",
                            "form_type": form,
                            "period_year": current_year,
                            "deadline_date": annual_deadline,
                            "company_id": company.id,
                        }
                    )

    @api.model
    def _cron_send_deadline_alerts(self):
        """Send alerts for deadlines due in 5 days or overdue"""
        today = fields.Date.today()
        upcoming = self.search(
            [
                ("state", "in", ("due_soon", "overdue")),
                ("return_id", "=", False),  # No return created yet
            ]
        )

        for deadline in upcoming:
            # Create activity for CFO/Finance Manager
            finance_users = self.env.ref("account.group_account_manager").users
            for user in finance_users:
                self.env["mail.activity"].create(
                    {
                        "res_model_id": self.env["ir.model"]
                        ._get("bir.filing.deadline")
                        .id,
                        "res_id": deadline.id,
                        "activity_type_id": self.env.ref(
                            "mail.mail_activity_data_warning"
                        ).id,
                        "summary": f"BIR Filing Due: {deadline.name}",
                        "note": f"Filing deadline: {deadline.deadline_date}. "
                        f"Status: {deadline.state}",
                        "user_id": user.id,
                        "date_deadline": deadline.deadline_date,
                    }
                )
