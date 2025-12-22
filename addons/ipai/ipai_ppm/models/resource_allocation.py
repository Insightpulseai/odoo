# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PpmResourceAllocation(models.Model):
    """Resource allocation tracking with overload detection."""

    _name = "ppm.resource.allocation"
    _description = "PPM Resource Allocation"
    _order = "date_start, employee_id"

    name = fields.Char(
        string="Description",
        compute="_compute_name",
        store=True,
    )

    # Resource
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        index=True,
    )
    user_id = fields.Many2one(
        related="employee_id.user_id",
        string="User",
        store=True,
    )

    # Scope
    program_id = fields.Many2one(
        "ppm.program",
        string="Program",
        index=True,
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        index=True,
    )
    task_id = fields.Many2one(
        "project.task",
        string="Task",
    )

    # Role
    role = fields.Selection(
        [
            ("lead", "Lead"),
            ("member", "Team Member"),
            ("reviewer", "Reviewer"),
            ("approver", "Approver"),
            ("consultant", "Consultant"),
            ("stakeholder", "Stakeholder"),
        ],
        string="Role",
        default="member",
    )

    # Dates
    date_start = fields.Date(
        string="Start Date",
        required=True,
    )
    date_end = fields.Date(
        string="End Date",
        required=True,
    )

    # Allocation
    allocation_pct = fields.Float(
        string="Allocation %",
        default=100.0,
        help="Percentage of employee capacity allocated (0-100+)",
    )
    planned_hours = fields.Float(
        string="Planned Hours",
        help="Total planned hours for this allocation period",
    )

    # Overload detection
    is_overloaded = fields.Boolean(
        string="Overloaded",
        compute="_compute_overload",
        store=True,
        help="True if employee total allocation exceeds 100%",
    )
    total_allocation = fields.Float(
        string="Total Allocation %",
        compute="_compute_overload",
        store=True,
        help="Sum of all allocations for this employee in the period",
    )

    # Status
    status = fields.Selection(
        [
            ("planned", "Planned"),
            ("confirmed", "Confirmed"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="planned",
    )

    notes = fields.Text(string="Notes")

    @api.depends("employee_id", "project_id", "program_id", "date_start")
    def _compute_name(self):
        for rec in self:
            parts = [rec.employee_id.name or "Employee"]
            if rec.project_id:
                parts.append(rec.project_id.name)
            elif rec.program_id:
                parts.append(rec.program_id.name)
            if rec.date_start:
                parts.append(str(rec.date_start))
            rec.name = " - ".join(parts)

    @api.depends("employee_id", "date_start", "date_end", "allocation_pct")
    def _compute_overload(self):
        for alloc in self:
            if not alloc.employee_id or not alloc.date_start or not alloc.date_end:
                alloc.total_allocation = alloc.allocation_pct
                alloc.is_overloaded = False
                continue

            # Find overlapping allocations for this employee
            overlapping = self.search(
                [
                    ("employee_id", "=", alloc.employee_id.id),
                    ("id", "!=", alloc.id if alloc.id else 0),
                    ("status", "not in", ["cancelled", "completed"]),
                    ("date_start", "<=", alloc.date_end),
                    ("date_end", ">=", alloc.date_start),
                ]
            )

            total = alloc.allocation_pct + sum(overlapping.mapped("allocation_pct"))
            alloc.total_allocation = total
            alloc.is_overloaded = total > 100

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError("End date must be after start date.")

    @api.constrains("allocation_pct")
    def _check_allocation(self):
        for rec in self:
            if rec.allocation_pct < 0:
                raise ValidationError("Allocation percentage cannot be negative.")
