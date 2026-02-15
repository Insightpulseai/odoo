# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models


class FinancePPMGoLiveChecklist(models.Model):
    _name = "ipai.finance.ppm.golive.checklist"
    _description = "Finance PPM Go-Live Checklist"
    _order = "create_date desc"

    name = fields.Char(
        string="Checklist Name", required=True, default="Finance PPM Go-Live"
    )
    version = fields.Char(string="Version", default="1.0.0")

    # Approval workflow (Finance Supervisor → Senior Supervisor Finance → Director)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("supervisor_review", "Finance Supervisor Review"),
            ("senior_supervisor_review", "Senior Supervisor Finance Review"),
            ("director_review", "Director Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        string="Status",
        tracking=True,
    )

    # Responsible parties
    supervisor_id = fields.Many2one("res.users", string="Finance Supervisor")
    supervisor_review_date = fields.Datetime(
        string="Supervisor Review Date", readonly=True
    )

    senior_supervisor_id = fields.Many2one(
        "res.users", string="Senior Supervisor Finance"
    )
    senior_supervisor_review_date = fields.Datetime(
        string="Senior Supervisor Review Date", readonly=True
    )

    director_id = fields.Many2one("res.users", string="Finance Director")
    director_review_date = fields.Datetime(string="Director Review Date", readonly=True)
    director_signoff_date = fields.Datetime(
        string="Director Sign-Off Date", readonly=True
    )

    # Sections
    section_ids = fields.Many2many(
        "ipai.finance.ppm.golive.section",
        string="Checklist Sections",
        help="9 section groups for go-live readiness",
    )

    # Progress tracking
    total_items = fields.Integer(
        string="Total Items", compute="_compute_progress", store=True
    )
    completed_items = fields.Integer(
        string="Completed Items", compute="_compute_progress", store=True
    )
    completion_pct = fields.Float(
        string="Completion %", compute="_compute_progress", store=True
    )

    # Audit fields
    created_by = fields.Many2one(
        "res.users",
        string="Created By",
        default=lambda self: self.env.user,
        readonly=True,
    )
    create_date = fields.Datetime(string="Creation Date", readonly=True)
    write_date = fields.Datetime(string="Last Updated", readonly=True)

    # Notes
    supervisor_notes = fields.Text(string="Finance Supervisor Notes")
    senior_supervisor_notes = fields.Text(string="Senior Supervisor Finance Notes")
    director_notes = fields.Text(string="Director Notes")

    @api.depends("section_ids.item_ids.is_checked")
    def _compute_progress(self):
        for record in self:
            all_items = record.section_ids.mapped("item_ids")
            record.total_items = len(all_items)
            record.completed_items = len(all_items.filtered(lambda x: x.is_checked))
            record.completion_pct = (
                (record.completed_items / record.total_items * 100)
                if record.total_items > 0
                else 0.0
            )

    def action_submit_to_supervisor(self):
        """Draft → Supervisor Review"""
        self.ensure_one()
        self.state = "supervisor_review"
        # Send notification to supervisor
        self.supervisor_id.notify_info(
            message=f"Finance PPM Go-Live Checklist ready for review",
            title="Go-Live Review Required",
        )

    def action_supervisor_approve(self):
        """Finance Supervisor Review → Senior Supervisor Finance Review"""
        self.ensure_one()
        self.state = "senior_supervisor_review"
        self.supervisor_review_date = datetime.now()
        # Send notification to senior supervisor
        self.senior_supervisor_id.notify_info(
            message=f"Finance PPM Go-Live Checklist approved by Finance Supervisor, needs Senior Supervisor review",
            title="Go-Live Review Required",
        )

    def action_senior_supervisor_approve(self):
        """Senior Supervisor Finance Review → Director Review"""
        self.ensure_one()
        self.state = "director_review"
        self.senior_supervisor_review_date = datetime.now()
        # Send notification to director
        self.director_id.notify_info(
            message=f"Finance PPM Go-Live Checklist approved by Senior Supervisor Finance, needs Director review",
            title="Go-Live Review Required",
        )

    def action_director_approve(self):
        """Director Review → Approved (Go-Live Authorized)"""
        self.ensure_one()
        if self.completion_pct < 100.0:
            raise UserError("Cannot approve: Checklist not 100% complete")
        self.state = "approved"
        self.director_review_date = datetime.now()
        self.director_signoff_date = datetime.now()
        # Send notification to all parties
        self.created_by.notify_info(
            message=f"Finance PPM Go-Live APPROVED by Director - System is GO LIVE",
            title="Go-Live Authorized",
        )

    def action_reject(self):
        """Reject checklist (any stage)"""
        self.ensure_one()
        self.state = "rejected"
        self.created_by.notify_warning(
            message=f"Finance PPM Go-Live Checklist REJECTED", title="Go-Live Rejected"
        )

    def action_reset_to_draft(self):
        """Reset to draft for corrections"""
        self.ensure_one()
        self.state = "draft"
        self.supervisor_review_date = False
        self.senior_supervisor_review_date = False
        self.director_review_date = False
        self.director_signoff_date = False
