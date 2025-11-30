# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FinanceTaskTemplate(models.Model):
    _name = "ipai.finance.task.template"
    _description = "Finance SSC Monthly Task Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Text(string="Task Description", required=True, tracking=True)

    category = fields.Selection(
        [
            ("payroll", "Payroll & Personnel"),
            ("tax", "Tax & Provisions"),
            ("vat", "VAT Data/Filing"),
            ("liquidation", "CA Liquidations"),
            ("accrual", "Accruals & Amortization"),
            ("reporting", "Regional Reporting"),
            ("compliance", "BIR Compliance"),
            ("wip", "WIP/OOP Reconciliation"),
            ("close", "Final Adjustments & Close"),
        ],
        string="Category",
        required=True,
        tracking=True,
    )

    description = fields.Text(string="Detailed Description")

    # Role Assignments
    employee_code_id = fields.Many2one(
        "ipai.finance.person", string="Owner", tracking=True
    )
    reviewed_by_id = fields.Many2one("ipai.finance.person", string="Reviewer")
    approved_by_id = fields.Many2one("ipai.finance.person", string="Approver")

    # SLA Durations
    prep_duration = fields.Float(string="Prep SLA (Days)", default=1.0)
    review_duration = fields.Float(string="Review SLA (Days)", default=0.5)
    approval_duration = fields.Float(string="Approval SLA (Days)", default=0.5)

    # Scheduling logic
    day_of_month = fields.Integer(
        string="Standard Day of Month", help="e.g. 27 for the 27th of every month"
    )
    trigger_type = fields.Selection(
        [
            ("fixed_date", "Fixed Date of Month"),
            ("bir_dependency", "Linked to BIR Deadline"),
        ],
        string="Trigger Type",
        default="fixed_date",
        required=True,
    )

    bir_form_id = fields.Many2one(
        "finance.bir.deadline",
        string="Related BIR Form",
        help="If trigger is BIR dependency, tasks are created based on this form's dates",
    )

    active = fields.Boolean(default=True)

    @api.model
    def cron_generate_daily_finance_tasks(self):
        """
        Run daily by Cron. Checks if any templates match 'today'
        or upcoming BIR deadlines and generates Project Tasks.
        """
        today = fields.Date.today()
        templates = self.search([("active", "=", True)])

        # Get or Create the main Finance Project
        Project = self.env["project.project"]
        project = Project.search([("name", "=", "Finance SSC Operations")], limit=1)
        if not project:
            project = Project.create(
                {
                    "name": "Finance SSC Operations",
                    "description": "Auto-generated project for Finance SSC tasks",
                }
            )
            _logger.info("Created Finance SSC Operations project")

        created_count = 0
        for template in templates:
            deadline = False

            # Logic 1: Fixed Day of Month (e.g., 27th of every month)
            if template.trigger_type == "fixed_date" and template.day_of_month:
                if today.day == template.day_of_month:
                    # Due tomorrow by default
                    deadline = today + timedelta(days=1)
                    _logger.info(
                        f"Template '{template.name}' triggered by fixed date "
                        f"(day {template.day_of_month})"
                    )

            # Logic 2: BIR Dependency (e.g., 4 days before deadline)
            elif template.trigger_type == "bir_dependency" and template.bir_form_id:
                bir_deadline = template.bir_form_id
                # If today matches the target prep date
                if bir_deadline.target_prep_date == today:
                    deadline = bir_deadline.deadline_date
                    _logger.info(
                        f"Template '{template.name}' triggered by BIR form "
                        f"'{bir_deadline.name}' prep date"
                    )

            # Create Task if triggered
            if deadline:
                self._create_finance_task(project, template, deadline)
                created_count += 1

        _logger.info(
            f"Finance task generation complete. Created {created_count} tasks."
        )
        return created_count

    def _create_finance_task(self, project, template, deadline):
        """Create a project task from the template."""
        Task = self.env["project.task"]

        # Find user based on employee code
        user_ids = []
        if template.employee_code_id and template.employee_code_id.user_id:
            user_ids = [(4, template.employee_code_id.user_id.id)]

        # Build task name with category prefix
        category_label = dict(self._fields["category"].selection).get(
            template.category, template.category
        )
        task_name = f"[{category_label}] {template.name}"

        # Check if task already exists for today (avoid duplicates)
        existing = Task.search(
            [
                ("project_id", "=", project.id),
                ("name", "=", task_name),
                ("date_deadline", "=", deadline),
            ],
            limit=1,
        )

        if existing:
            _logger.info(f"Task '{task_name}' already exists, skipping creation")
            return existing

        task_vals = {
            "name": task_name,
            "project_id": project.id,
            "description": template.description or template.name,
            "date_deadline": deadline,
            "user_ids": user_ids,
        }

        task = Task.create(task_vals)
        _logger.info(f"Created task: {task_name} (ID: {task.id})")
        return task

    @api.model
    def generate_tasks_for_bir_deadline(self, bir_deadline_id):
        """Manually generate tasks for a specific BIR deadline."""
        bir_deadline = self.env["finance.bir.deadline"].browse(bir_deadline_id)
        if not bir_deadline.exists():
            return False

        templates = self.search(
            [
                ("active", "=", True),
                ("trigger_type", "=", "bir_dependency"),
                ("bir_form_id", "=", bir_deadline_id),
            ]
        )

        Project = self.env["project.project"]
        project = Project.search([("name", "=", "Finance SSC Operations")], limit=1)
        if not project:
            project = Project.create(
                {
                    "name": "Finance SSC Operations",
                    "description": "Auto-generated project for Finance SSC tasks",
                }
            )

        created_tasks = self.env["project.task"]
        for template in templates:
            task = self._create_finance_task(
                project, template, bir_deadline.deadline_date
            )
            if task:
                created_tasks |= task

        return created_tasks
