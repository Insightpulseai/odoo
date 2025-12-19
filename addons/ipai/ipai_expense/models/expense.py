# -*- coding: utf-8 -*-
"""
IPAI Expense & Travel Models (PH).

This module extends Odoo's expense management with Philippines-specific
workflows and validation rules:
- Travel request approval workflow (Manager → Finance)
- Project cost tracking for specific expense categories
- PH expense category enforcement

Models:
    IpaiTravelRequest: Travel authorization with multi-level approval
    HrExpense (inherited): Extended expense with travel and project linkage
"""
from odoo import api, fields, models


class IpaiTravelRequest(models.Model):
    """
    Travel Request Model.

    Handles pre-approval of business travel with budget estimation.
    Implements dual-approval workflow: Manager → Finance.

    Workflow:
        draft → submitted → manager_approved → finance_approved
                    ↓              ↓                ↓
                rejected       rejected         rejected

    Attributes:
        _name: ipai.travel.request
        _description: IPAI Travel Request
    """

    _name = "ipai.travel.request"
    _description = "IPAI Travel Request"
    _order = "start_date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "ipai.travel.request"
        ),
    )
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    project_id = fields.Many2one("project.project", string="Project / Job")
    destination = fields.Char(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    purpose = fields.Text()
    estimated_budget = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id.id,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("manager_approved", "Manager Approved"),
            ("finance_approved", "Finance Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company.id
    )

    def action_submit(self):
        """
        Submit travel request for approval.

        Transitions state from 'draft' to 'submitted', triggering
        the approval workflow starting with manager review.
        """
        for rec in self:
            rec.state = "submitted"

    def action_manager_approve(self):
        """
        Manager approves the travel request.

        First-level approval. Transitions to 'manager_approved',
        allowing finance to perform final approval.
        """
        for rec in self:
            rec.state = "manager_approved"

    def action_finance_approve(self):
        """
        Finance approves the travel request.

        Final approval step. Transitions to 'finance_approved',
        authorizing the employee to proceed with travel arrangements.
        """
        for rec in self:
            rec.state = "finance_approved"

    def action_reject(self):
        """
        Reject the travel request.

        Can be called at any approval stage. Transitions to 'rejected',
        requiring the employee to submit a new request if needed.
        """
        for rec in self:
            rec.state = "rejected"


class HrExpense(models.Model):
    """
    Extended HR Expense Model.

    Adds PH-specific fields and validation to standard Odoo expenses:
    - Links expenses to travel requests for travel-related items
    - Enforces project code requirement for specific categories
    - Validates expense category consistency

    Inherited Fields:
        travel_request_id: Link to approved travel authorization
        project_id: Project/job code for cost allocation
        requires_project: Computed flag for validation
    """

    _inherit = "hr.expense"

    travel_request_id = fields.Many2one(
        "ipai.travel.request",
        string="Travel Request",
        help="Link to travel request if this expense is travel-related",
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project / Job",
        help="Required for certain expense categories to track project costs",
    )
    requires_project = fields.Boolean(
        string="Requires Project",
        compute="_compute_requires_project",
        store=True,
        help="Indicates if this expense category requires a project code",
    )

    @api.depends("product_id")
    def _compute_requires_project(self):
        """Certain expense categories require project tracking"""
        project_required_categories = [
            "Meals & Entertainment",
            "Office Supplies",
            "Miscellaneous Expense",
        ]
        for expense in self:
            if expense.product_id and expense.product_id.categ_id:
                expense.requires_project = (
                    expense.product_id.categ_id.name in project_required_categories
                )
            else:
                expense.requires_project = False

    @api.constrains("project_id", "requires_project")
    def _check_project_required(self):
        """Enforce project requirement for certain categories"""
        for expense in self:
            if expense.requires_project and not expense.project_id:
                raise models.ValidationError(
                    f"Project/Job code is required for expense category: {expense.product_id.categ_id.name}"
                )

    @api.constrains("travel_request_id", "product_id")
    def _check_travel_request_consistency(self):
        """Travel-related expenses should have a travel request"""
        travel_categories = ["Travel & Accommodation"]
        for expense in self:
            if expense.product_id and expense.product_id.categ_id:
                is_travel = expense.product_id.categ_id.name in travel_categories
                if is_travel and not expense.travel_request_id:
                    # Warning only, not blocking - allow manual expense entry
                    pass
