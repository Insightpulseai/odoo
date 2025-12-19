# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProjectTask(models.Model):
    _inherit = "project.task"

    ipai_task_category = fields.Selection([
        ("payroll", "Payroll & Personnel"),
        ("tax", "Tax & Provisions"),
        ("rent", "Rent & Leases"),
        ("accruals", "Accruals & Expenses"),
        ("billing", "Client Billings / WIP / OOP"),
        ("treasury", "Treasury"),
        ("vat", "VAT / Indirect Tax"),
        ("interco", "Intercompany"),
        ("review", "Prior Period Review"),
        ("reporting", "Regional Reporting"),
        ("other", "Other"),
    ], default="other", index=True)

    ipai_template_id = fields.Many2one("ipai.finance.task.template", string="Template", index=True, ondelete="set null")

    ipai_owner_code = fields.Char(string="Owner Code", index=True)
    ipai_owner_role = fields.Selection([("prep", "Preparation"), ("review", "Review"), ("approve", "Approval")], index=True)
    ipai_compliance_step = fields.Selection([("prepare", "Prepare"), ("review", "Review"), ("approve", "Approve/Pay"), ("file", "File/Pay")], index=True)

    ipai_days_to_deadline = fields.Integer(compute="_compute_ipai_deadline_metrics", store=True)
    ipai_status_bucket = fields.Selection([
        ("overdue", "Overdue"),
        ("due_soon", "Due Soon (<=3d)"),
        ("on_track", "On Track"),
        ("no_deadline", "No Deadline"),
    ], compute="_compute_ipai_deadline_metrics", store=True, index=True)

    @api.depends("date_deadline")
    def _compute_ipai_deadline_metrics(self):
        today = fields.Date.today()
        for t in self:
            if not t.date_deadline:
                t.ipai_days_to_deadline = 0
                t.ipai_status_bucket = "no_deadline"
                continue
            delta = (t.date_deadline - today).days
            t.ipai_days_to_deadline = delta
            if delta < 0:
                t.ipai_status_bucket = "overdue"
            elif delta <= 3:
                t.ipai_status_bucket = "due_soon"
            else:
                t.ipai_status_bucket = "on_track"
