# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Engagement(models.Model):
    """Client engagement for accounting services."""
    _name = "ipai.engagement"
    _description = "IPAI Accounting Engagement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "fiscal_year desc, partner_id"

    name = fields.Char(
        string="Engagement Reference",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Client",
        required=True,
        tracking=True,
        domain="[('is_company', '=', True)]",
    )

    engagement_type = fields.Selection([
        ("bookkeeping", "Bookkeeping"),
        ("tax_prep", "Tax Preparation"),
        ("tax_planning", "Tax Planning"),
        ("audit", "Audit"),
        ("review", "Review"),
        ("compilation", "Compilation"),
        ("advisory", "Advisory/Consulting"),
        ("payroll", "Payroll Services"),
        ("forensic", "Forensic Accounting"),
    ], string="Engagement Type", required=True, tracking=True)

    fiscal_year = fields.Char(
        string="Fiscal Year",
        required=True,
        tracking=True,
        help="e.g., 2024, FY2024, CY2024",
    )

    fiscal_year_start = fields.Date(string="Fiscal Year Start")
    fiscal_year_end = fields.Date(string="Fiscal Year End")

    state = fields.Selection([
        ("draft", "Draft"),
        ("planning", "Planning"),
        ("fieldwork", "Fieldwork"),
        ("review", "Review"),
        ("reporting", "Reporting"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ], string="Status", default="draft", tracking=True)

    billing_mode = fields.Selection([
        ("fixed", "Fixed Fee"),
        ("hourly", "Hourly"),
        ("retainer", "Retainer"),
        ("value", "Value-Based"),
    ], string="Billing Mode", default="hourly", tracking=True)

    estimated_fee = fields.Monetary(
        string="Estimated Fee",
        currency_field="currency_id",
        tracking=True,
    )

    actual_fee = fields.Monetary(
        string="Actual Fee",
        currency_field="currency_id",
        compute="_compute_actual_fee",
        store=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    project_id = fields.Many2one(
        "project.project",
        string="Delivery Project",
        tracking=True,
    )

    manager_id = fields.Many2one(
        "res.users",
        string="Engagement Manager",
        tracking=True,
    )

    partner_in_charge_id = fields.Many2one(
        "res.users",
        string="Partner in Charge",
        tracking=True,
    )

    # Related records
    period_ids = fields.One2many(
        "ipai.engagement.period",
        "engagement_id",
        string="Periods",
    )

    compliance_task_ids = fields.One2many(
        "ipai.compliance.task",
        "engagement_id",
        string="Compliance Tasks",
    )

    document_request_ids = fields.One2many(
        "ipai.document.request",
        "engagement_id",
        string="Document Requests",
    )

    workpaper_ids = fields.One2many(
        "ipai.workpaper",
        "engagement_id",
        string="Workpapers",
    )

    description = fields.Html(string="Description")
    notes = fields.Text(string="Internal Notes")

    # Computed fields
    period_count = fields.Integer(compute="_compute_counts", store=True)
    compliance_count = fields.Integer(compute="_compute_counts", store=True)
    document_request_count = fields.Integer(compute="_compute_counts", store=True)
    workpaper_count = fields.Integer(compute="_compute_counts", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "ipai.engagement"
                ) or _("New")
        return super().create(vals_list)

    @api.depends("period_ids", "compliance_task_ids", "document_request_ids", "workpaper_ids")
    def _compute_counts(self):
        for engagement in self:
            engagement.period_count = len(engagement.period_ids)
            engagement.compliance_count = len(engagement.compliance_task_ids)
            engagement.document_request_count = len(engagement.document_request_ids)
            engagement.workpaper_count = len(engagement.workpaper_ids)

    @api.depends("workpaper_ids.billable_hours")
    def _compute_actual_fee(self):
        for engagement in self:
            # This is a simplified calculation - can be extended
            # to pull from timesheets or invoices
            engagement.actual_fee = sum(
                engagement.workpaper_ids.mapped("billable_hours")
            ) * 150  # Default rate

    @api.constrains("fiscal_year_start", "fiscal_year_end")
    def _check_fiscal_dates(self):
        for engagement in self:
            if engagement.fiscal_year_start and engagement.fiscal_year_end:
                if engagement.fiscal_year_end < engagement.fiscal_year_start:
                    raise ValidationError(
                        _("Fiscal year end must be after fiscal year start.")
                    )

    def action_start_planning(self):
        self.write({"state": "planning"})

    def action_start_fieldwork(self):
        self.write({"state": "fieldwork"})

    def action_start_review(self):
        self.write({"state": "review"})

    def action_start_reporting(self):
        self.write({"state": "reporting"})

    def action_complete(self):
        self.write({"state": "completed"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_view_workpapers(self):
        """Open workpapers for this engagement."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Workpapers"),
            "res_model": "ipai.workpaper",
            "view_mode": "list,form",
            "domain": [("engagement_id", "=", self.id)],
            "context": {"default_engagement_id": self.id},
        }

    def action_view_compliance(self):
        """Open compliance tasks for this engagement."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Compliance Tasks"),
            "res_model": "ipai.compliance.task",
            "view_mode": "list,form,kanban",
            "domain": [("engagement_id", "=", self.id)],
            "context": {"default_engagement_id": self.id},
        }

    def action_view_document_requests(self):
        """Open document requests for this engagement."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Document Requests"),
            "res_model": "ipai.document.request",
            "view_mode": "list,form",
            "domain": [("engagement_id", "=", self.id)],
            "context": {"default_engagement_id": self.id},
        }


class EngagementPeriod(models.Model):
    """Engagement periods for tracking work across time."""
    _name = "ipai.engagement.period"
    _description = "IPAI Engagement Period"
    _order = "period_start"

    engagement_id = fields.Many2one(
        "ipai.engagement",
        string="Engagement",
        required=True,
        ondelete="cascade",
    )

    name = fields.Char(
        string="Period Name",
        compute="_compute_name",
        store=True,
    )

    period_start = fields.Date(string="Period Start", required=True)
    period_end = fields.Date(string="Period End", required=True)

    close_status = fields.Selection([
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("pending_review", "Pending Review"),
        ("closed", "Closed"),
    ], string="Close Status", default="open")

    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer",
    )

    review_date = fields.Date(string="Review Date")
    close_date = fields.Date(string="Close Date")

    notes = fields.Text(string="Notes")

    @api.depends("period_start", "period_end")
    def _compute_name(self):
        for period in self:
            if period.period_start and period.period_end:
                period.name = f"{period.period_start.strftime('%b %Y')} - {period.period_end.strftime('%b %Y')}"
            else:
                period.name = "New Period"

    @api.constrains("period_start", "period_end")
    def _check_dates(self):
        for period in self:
            if period.period_end < period.period_start:
                raise ValidationError(_("Period end must be after period start."))

    def action_start_work(self):
        self.write({"close_status": "in_progress"})

    def action_submit_review(self):
        self.write({"close_status": "pending_review"})

    def action_close(self):
        self.write({
            "close_status": "closed",
            "close_date": fields.Date.today(),
        })
