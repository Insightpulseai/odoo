# -*- coding: utf-8 -*-
"""Wizard to generate month-end close project."""
from datetime import date

from odoo import fields, models


class IpaCloseGenerateWizard(models.TransientModel):
    _name = "ipai.finance.close.generate.wizard"
    _description = "Generate Month-End Close Project"

    year = fields.Integer(default=lambda self: date.today().year, required=True)
    month = fields.Integer(default=lambda self: date.today().month, required=True)
    calendar_id = fields.Many2one(
        "resource.calendar", string="Working Calendar", required=False
    )

    def action_generate(self):
        """Generate the month-end close project."""
        self.ensure_one()
        res = (
            self.env["ipai.finance.close.service"]
            .sudo()
            .generate_month_close(
                self.year,
                self.month,
                calendar_id=self.calendar_id.id if self.calendar_id else None,
            )
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "res_id": res["project_id"],
            "view_mode": "form",
            "target": "current",
        }
