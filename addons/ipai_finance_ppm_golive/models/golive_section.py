# -*- coding: utf-8 -*-
from odoo import api, fields, models


class FinancePPMGoLiveSection(models.Model):
    _name = "ipai.finance.ppm.golive.section"
    _description = "Go-Live Checklist Section"
    _order = "sequence, name"

    name = fields.Char(string="Section Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Text(string="Description")

    # Section type (9 predefined categories)
    section_type = fields.Selection(
        [
            ("data_system", "Data & System Readiness"),
            ("module", "Finance PPM Module Readiness"),
            ("afc", "AFC (Financial Close) Go-Live"),
            ("stc", "STC (Tax Compliance) Go-Live"),
            ("control_room", "Control Room (AI/Automation) Go-Live"),
            ("notion_parity", "Notion-AI Parity Check"),
            ("audit_compliance", "Audit & Compliance Check"),
            ("operational", "Operational Check"),
            ("golive_criteria", "Official Go-Live Criteria"),
        ],
        string="Section Type",
        required=True,
    )

    # Related checklist items
    item_ids = fields.One2many(
        "ipai.finance.ppm.golive.item", "section_id", string="Checklist Items"
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

    @api.depends("item_ids.is_checked")
    def _compute_progress(self):
        for record in self:
            record.total_items = len(record.item_ids)
            record.completed_items = len(
                record.item_ids.filtered(lambda x: x.is_checked)
            )
            record.completion_pct = (
                (record.completed_items / record.total_items * 100)
                if record.total_items > 0
                else 0.0
            )
