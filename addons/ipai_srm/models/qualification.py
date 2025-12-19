# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SrmQualification(models.Model):
    """Supplier qualification/onboarding process."""

    _name = "srm.qualification"
    _description = "Supplier Qualification"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        compute="_compute_name",
        store=True,
    )
    supplier_id = fields.Many2one(
        "srm.supplier",
        required=True,
        tracking=True,
    )

    # Process
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("documents", "Document Collection"),
            ("review", "Under Review"),
            ("site_visit", "Site Visit"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        tracking=True,
    )
    qualification_type = fields.Selection(
        [
            ("initial", "Initial Qualification"),
            ("requalification", "Re-qualification"),
            ("scope_expansion", "Scope Expansion"),
        ],
        default="initial",
        required=True,
    )

    # Dates
    start_date = fields.Date(default=fields.Date.today)
    target_completion = fields.Date()
    completion_date = fields.Date()
    expiry_date = fields.Date()

    # Evaluation
    reviewer_id = fields.Many2one("res.users")
    approver_id = fields.Many2one("res.users")
    approval_date = fields.Datetime()

    # Checklist
    checklist_ids = fields.One2many("srm.qualification.checklist", "qualification_id")
    checklist_complete = fields.Boolean(compute="_compute_checklist_complete")

    # Documents
    document_ids = fields.Many2many("ir.attachment", string="Documents")

    # Risk Assessment
    risk_score = fields.Float()
    risk_notes = fields.Text()

    # Notes
    notes = fields.Text()
    rejection_reason = fields.Text()

    @api.depends("supplier_id", "qualification_type", "start_date")
    def _compute_name(self):
        for rec in self:
            if rec.supplier_id:
                rec.name = f"{rec.supplier_id.name} - {rec.qualification_type} ({rec.start_date})"
            else:
                rec.name = "New Qualification"

    @api.depends("checklist_ids", "checklist_ids.is_complete")
    def _compute_checklist_complete(self):
        for rec in self:
            if rec.checklist_ids:
                rec.checklist_complete = all(rec.checklist_ids.mapped("is_complete"))
            else:
                rec.checklist_complete = False

    def action_start_documents(self):
        for rec in self:
            rec.state = "documents"
            rec.supplier_id.state = "qualification"

    def action_submit_review(self):
        for rec in self:
            rec.state = "review"

    def action_schedule_site_visit(self):
        for rec in self:
            rec.state = "site_visit"

    def action_approve(self):
        for rec in self:
            rec.write({
                "state": "approved",
                "approver_id": self.env.user.id,
                "approval_date": fields.Datetime.now(),
                "completion_date": fields.Date.today(),
            })
            rec.supplier_id.write({
                "state": "active",
                "is_qualified": True,
            })

    def action_reject(self):
        for rec in self:
            rec.state = "rejected"


class SrmQualificationChecklist(models.Model):
    """Qualification checklist item."""

    _name = "srm.qualification.checklist"
    _description = "Qualification Checklist"
    _order = "sequence"

    qualification_id = fields.Many2one(
        "srm.qualification",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    description = fields.Text()
    is_required = fields.Boolean(default=True)
    is_complete = fields.Boolean(default=False)
    completed_by = fields.Many2one("res.users")
    completed_date = fields.Date()
    notes = fields.Text()

    def action_mark_complete(self):
        for rec in self:
            rec.write({
                "is_complete": True,
                "completed_by": self.env.user.id,
                "completed_date": fields.Date.today(),
            })
