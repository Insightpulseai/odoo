# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTaskFinance(models.Model):
    _inherit = "project.task"

    finance_code = fields.Char(
        string="Role Code",
        help="Finance functional code, e.g. RIM, BOM",
    )
    approver_id = fields.Many2one(
        "res.users",
        string="Accountable (Approver)",
        help="Final authority for the finance task",
    )
    reviewer_id = fields.Many2one(
        "res.users",
        string="Consulted (Reviewer)",
        help="Reviewer consulted before approval",
    )
    finance_deadline_type = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
        ],
        string="Frequency",
    )
    finance_logframe_id = fields.Many2one(
        "ipai.finance.logframe",
        string="Logframe Entry",
        help="Link to Finance Logical Framework objective",
    )
    bir_schedule_id = fields.Many2one(
        "ipai.finance.bir_schedule",
        string="BIR Form",
        help="Link to BIR Filing Schedule",
    )
    is_finance_ppm = fields.Boolean(
        compute="_compute_is_finance_ppm",
        store=True,
        string="Is Finance PPM Task",
    )

    @api.depends(
        "finance_logframe_id",
        "bir_schedule_id",
        "finance_code",
        "approver_id",
        "reviewer_id",
        "finance_deadline_type",
    )
    def _compute_is_finance_ppm(self):
        for task in self:
            task.is_finance_ppm = bool(
                task.finance_logframe_id
                or task.bir_schedule_id
                or task.finance_code
                or task.approver_id
                or task.reviewer_id
                or task.finance_deadline_type
            )
