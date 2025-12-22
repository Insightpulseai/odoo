# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BirScheduleLine(models.Model):
    _name = "ipai.bir.schedule.line"
    _description = "BIR Schedule Line"
    _order = "deadline_date, bir_form"

    bir_form = fields.Char(required=True, index=True)
    period_label = fields.Char(
        required=True, help="e.g., 'Jan 2026' or 'Q1 2026' or 'FY 2025'"
    )
    deadline_date = fields.Date(required=True, index=True)

    prep_by_code = fields.Char(string="Prepared by (code)")
    review_by_code = fields.Char(string="Reviewed by (code)")
    approve_by_code = fields.Char(string="Approved by (code)")

    prep_due_date = fields.Date()
    review_due_date = fields.Date()
    approve_due_date = fields.Date()

    notes = fields.Char()

    _sql_constraints = [
        (
            "bir_sched_unique",
            "unique(bir_form, period_label)",
            "BIR form+period must be unique.",
        ),
    ]

    @api.constrains(
        "deadline_date", "prep_due_date", "review_due_date", "approve_due_date"
    )
    def _check_dates(self):
        for rec in self:
            for d in [rec.prep_due_date, rec.review_due_date, rec.approve_due_date]:
                if d and rec.deadline_date and d > rec.deadline_date:
                    raise ValidationError(
                        _("Step dates must not be after the filing deadline.")
                    )

    @api.model
    def _upsert_from_seed(self, row: dict, strict: bool = False):
        bir_form = (row or {}).get("bir_form")
        period_label = (row or {}).get("period_label")
        if not bir_form or not period_label:
            if strict:
                raise ValidationError(
                    _("Seed BIR schedule row missing bir_form/period_label.")
                )
            return False
        vals = {
            "deadline_date": (row or {}).get("deadline_date"),
            "prep_by_code": (row or {}).get("prep_by_code"),
            "review_by_code": (row or {}).get("review_by_code"),
            "approve_by_code": (row or {}).get("approve_by_code"),
            "prep_due_date": (row or {}).get("prep_due_date"),
            "review_due_date": (row or {}).get("review_due_date"),
            "approve_due_date": (row or {}).get("approve_due_date"),
            "notes": (row or {}).get("notes"),
        }
        rec = self.search(
            [("bir_form", "=", bir_form), ("period_label", "=", period_label)], limit=1
        )
        if rec:
            rec.write(vals)
            return rec
        vals.update({"bir_form": bir_form, "period_label": period_label})
        return self.create(vals)
