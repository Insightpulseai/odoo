# -*- coding: utf-8 -*-
"""Month-End Template models for task generation."""
from datetime import date, timedelta

from odoo.addons.ipai_project_program.utils.date_utils import subtract_business_days

from odoo import api, fields, models


class IPAIMonthEndTemplate(models.Model):
    _name = "ipai.month.end.template"
    _description = "Month-End Template"
    _order = "category, task_base_name"

    category = fields.Char(
        string="Category",
        help="Template category (e.g., Payroll & Personnel, Accruals)",
    )
    task_base_name = fields.Char(
        string="Task Base Name",
        required=True,
        index=True,
        help="Base name for generated tasks",
    )
    default_im_xml_id = fields.Char(
        string="Default IM XML ID",
        help="XMLID of IM project to receive generated tasks",
    )
    step_ids = fields.One2many(
        "ipai.month.end.template.step",
        "template_id",
        string="Steps",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _sql_constraints = [
        (
            "task_base_name_unique",
            "unique(task_base_name)",
            "Task base name must be unique!",
        ),
    ]


class IPAIMonthEndTemplateStep(models.Model):
    _name = "ipai.month.end.template.step"
    _description = "Month-End Template Step"
    _order = "template_id, sequence"

    template_id = fields.Many2one(
        "ipai.month.end.template",
        string="Template",
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
    offset_days = fields.Integer(
        string="Offset Days",
        default=0,
        help="Calendar-day offset from anchor date (negative means earlier)",
    )
    business_days_before = fields.Integer(
        string="Business Days Before",
        default=0,
        help="Alternative: business days before anchor date",
    )

    def compute_target_date(self, anchor: date) -> date:
        """
        Compute target date for this step relative to anchor.

        Args:
            anchor: The anchor date (e.g., month-end close date)

        Returns:
            Computed target date for this step
        """
        self.ensure_one()
        if self.business_days_before and self.business_days_before > 0:
            return subtract_business_days(anchor, self.business_days_before)
        # Calendar day offset
        return anchor + timedelta(days=self.offset_days or 0)
