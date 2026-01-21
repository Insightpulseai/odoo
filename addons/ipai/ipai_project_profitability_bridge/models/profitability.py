# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiProjectProfitability(models.Model):
    _name = "ipai.project.profitability"
    _description = "IPAI Project Profitability"
    _rec_name = "project_id"
    _order = "project_id"

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        index=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id",
        store=True,
    )

    # KPI fields
    cost = fields.Monetary(
        string="Total Cost",
        readonly=True,
        help="Sum of negative analytic line amounts (costs).",
    )
    revenue = fields.Monetary(
        string="Total Revenue",
        readonly=True,
        help="Sum of positive analytic line amounts (revenues).",
    )
    margin = fields.Monetary(
        string="Margin",
        readonly=True,
        help="Revenue - Cost.",
    )
    margin_pct = fields.Float(
        string="Margin %",
        readonly=True,
        help="Margin as percentage of revenue.",
    )

    # Timesheet specific
    timesheet_cost = fields.Monetary(
        string="Timesheet Cost",
        readonly=True,
        help="Cost from timesheet entries only.",
    )
    timesheet_hours = fields.Float(
        string="Timesheet Hours",
        readonly=True,
        help="Total hours from timesheet entries.",
    )

    # Metadata
    last_computed_at = fields.Datetime(
        string="Last Computed",
        readonly=True,
    )
    analytic_line_count = fields.Integer(
        string="Analytic Lines",
        readonly=True,
        help="Number of analytic lines considered.",
    )

    _sql_constraints = [
        (
            "uniq_project_company",
            "unique(project_id, company_id)",
            "Profitability row already exists for this project/company.",
        ),
    ]

    @api.model
    def recompute_all(self, company_id=None):
        """
        Recompute profitability KPIs for all projects in a company.

        Convention:
        - Negative amounts => Cost
        - Positive amounts => Revenue
        """
        company = (
            self.env["res.company"].browse(company_id)
            if company_id
            else self.env.company
        )
        Project = self.env["project.project"].with_company(company)
        AAL = self.env["account.analytic.line"].with_company(company)

        projects = Project.search([("company_id", "=", company.id)])
        if not projects:
            return 0

        # Get all analytic lines for projects
        # Use project_id field (from hr_timesheet or similar)
        lines = AAL.search([("project_id", "in", projects.ids)])

        # Group by project
        by_project = {}
        for line in lines:
            pid = line.project_id.id
            if pid not in by_project:
                by_project[pid] = {
                    "lines": [],
                    "total": 0.0,
                    "timesheet_cost": 0.0,
                    "timesheet_hours": 0.0,
                }
            by_project[pid]["lines"].append(line)
            by_project[pid]["total"] += line.amount or 0.0

            # Check if it's a timesheet entry (has unit_amount)
            if line.unit_amount:
                by_project[pid]["timesheet_hours"] += line.unit_amount
                if line.amount < 0:
                    by_project[pid]["timesheet_cost"] += abs(line.amount)

        now = fields.Datetime.now()
        updated = 0

        for project in projects:
            data = by_project.get(project.id, {})
            total = data.get("total", 0.0)
            line_count = len(data.get("lines", []))

            # Convention: negative = cost, positive = revenue
            revenue = total if total > 0 else 0.0
            cost = abs(total) if total < 0 else 0.0

            # If we have both costs and revenues, need to sum them separately
            if data.get("lines"):
                revenue = sum(l.amount for l in data["lines"] if (l.amount or 0) > 0)
                cost = abs(sum(l.amount for l in data["lines"] if (l.amount or 0) < 0))

            margin = revenue - cost
            margin_pct = (margin / revenue * 100.0) if revenue else 0.0

            vals = {
                "project_id": project.id,
                "company_id": company.id,
                "revenue": revenue,
                "cost": cost,
                "margin": margin,
                "margin_pct": margin_pct,
                "timesheet_cost": data.get("timesheet_cost", 0.0),
                "timesheet_hours": data.get("timesheet_hours", 0.0),
                "analytic_line_count": line_count,
                "last_computed_at": now,
            }

            rec = self.search(
                [("project_id", "=", project.id), ("company_id", "=", company.id)],
                limit=1,
            )
            if rec:
                rec.write(vals)
            else:
                self.create(vals)
            updated += 1

        return updated

    @api.model
    def recompute_for_project(self, project_id):
        """Recompute KPIs for a single project."""
        project = self.env["project.project"].browse(project_id)
        if not project.exists():
            return False

        AAL = self.env["account.analytic.line"]
        lines = AAL.search([("project_id", "=", project_id)])

        revenue = sum(l.amount for l in lines if (l.amount or 0) > 0)
        cost = abs(sum(l.amount for l in lines if (l.amount or 0) < 0))
        margin = revenue - cost
        margin_pct = (margin / revenue * 100.0) if revenue else 0.0

        timesheet_hours = sum(l.unit_amount or 0 for l in lines)
        timesheet_cost = abs(
            sum(l.amount for l in lines if l.unit_amount and (l.amount or 0) < 0)
        )

        vals = {
            "project_id": project_id,
            "company_id": project.company_id.id,
            "revenue": revenue,
            "cost": cost,
            "margin": margin,
            "margin_pct": margin_pct,
            "timesheet_cost": timesheet_cost,
            "timesheet_hours": timesheet_hours,
            "analytic_line_count": len(lines),
            "last_computed_at": fields.Datetime.now(),
        }

        rec = self.search(
            [
                ("project_id", "=", project_id),
                ("company_id", "=", project.company_id.id),
            ],
            limit=1,
        )
        if rec:
            rec.write(vals)
        else:
            self.create(vals)

        return True

    def action_recompute(self):
        """Button action to recompute selected records."""
        for rec in self:
            self.recompute_for_project(rec.project_id.id)
        return True

    @api.model
    def cron_recompute_all(self):
        """Scheduled action to recompute all companies."""
        companies = self.env["res.company"].search([])
        for company in companies:
            self.recompute_all(company_id=company.id)
