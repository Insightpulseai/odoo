# -*- coding: utf-8 -*-
"""BIR Schedule Item models for tax filing task generation."""
from datetime import date
from odoo import fields, models
from odoo.addons.ipai_project_program.utils.date_utils import subtract_business_days


class IPAIBIRScheduleItem(models.Model):
    _name = "ipai.bir.schedule.item"
    _description = "BIR Schedule Item"
    _order = "deadline, bir_form, period_covered"

    bir_form = fields.Char(
        string="BIR Form",
        required=True,
        index=True,
        help="BIR form number (e.g., 1601-C, 2550M)",
    )
    period_covered = fields.Char(
        string="Period Covered",
        required=True,
        index=True,
        help="Period covered by this filing (e.g., Dec 2025)",
    )
    deadline = fields.Date(
        string="Filing Deadline",
        required=True,
        index=True,
        help="Statutory filing deadline",
    )
    im_xml_id = fields.Char(
        string="Target IM XML ID",
        required=True,
        help="Target IM project XMLID (usually IM2)",
    )
    step_ids = fields.One2many(
        "ipai.bir.schedule.step",
        "item_id",
        string="Steps",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _sql_constraints = [
        ("bir_schedule_unique", "unique(bir_form, period_covered, deadline)",
         "BIR schedule item must be unique per form/period/deadline!"),
    ]


class IPAIBIRScheduleStep(models.Model):
    _name = "ipai.bir.schedule.step"
    _description = "BIR Schedule Step"
    _order = "item_id, sequence"

    item_id = fields.Many2one(
        "ipai.bir.schedule.item",
        string="Schedule Item",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    activity_type = fields.Selection(
        [
            ("prep", "Preparation"),
            ("review", "Review"),
            ("approve", "Approval"),
            ("file", "Filing"),
        ],
        string="Activity Type",
        required=True,
    )
    role_code = fields.Char(
        string="Role Code",
        help="Directory code for assignment (e.g., RIM, BOM, CKVC)",
    )
    business_days_before = fields.Integer(
        string="Business Days Before",
        default=0,
        help="Business days before deadline",
    )
    on_or_before_deadline = fields.Boolean(
        string="On/Before Deadline",
        default=False,
        help="If True, target date is the deadline itself",
    )

    def compute_target_date(self, deadline: date) -> date:
        """
        Compute target date for this step relative to deadline.

        Args:
            deadline: The filing deadline date

        Returns:
            Computed target date for this step
        """
        self.ensure_one()
        if self.on_or_before_deadline or self.activity_type == "file":
            return deadline
        if self.business_days_before and self.business_days_before > 0:
            return subtract_business_days(deadline, self.business_days_before)
        return deadline
