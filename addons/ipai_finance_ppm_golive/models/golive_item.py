# -*- coding: utf-8 -*-
from odoo import api, fields, models


class FinancePPMGoLiveItem(models.Model):
    _name = "ipai.finance.ppm.golive.item"
    _description = "Go-Live Checklist Item"
    _order = "section_id, sequence, name"

    name = fields.Char(string="Checklist Item", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Text(string="Acceptance Criteria")

    # Parent section
    section_id = fields.Many2one(
        "ipai.finance.ppm.golive.section",
        string="Section",
        required=True,
        ondelete="cascade",
    )

    # Completion tracking
    is_checked = fields.Boolean(string="Completed", default=False)
    checked_by = fields.Many2one("res.users", string="Checked By", readonly=True)
    checked_date = fields.Datetime(string="Checked Date", readonly=True)

    # Evidence/notes
    notes = fields.Text(string="Notes")
    evidence_url = fields.Char(
        string="Evidence URL", help="Link to supporting documentation or screenshot"
    )

    # Priority
    is_critical = fields.Boolean(
        string="Critical", default=False, help="Blocking item for go-live"
    )

    def action_mark_complete(self):
        """Mark item as completed with timestamp and user"""
        self.ensure_one()
        self.is_checked = True
        self.checked_by = self.env.user
        self.checked_date = fields.Datetime.now()

    def action_mark_incomplete(self):
        """Unmark item"""
        self.ensure_one()
        self.is_checked = False
        self.checked_by = False
        self.checked_date = False
