# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FinanceTaskTemplate(models.Model):
    _name = "ipai.finance.task.template"
    _description = "Finance Task Template (Month-End / Compliance)"
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    category = fields.Selection(
        [
            ("month_end", "Month-End Close"),
            ("bir", "BIR / Tax Compliance"),
            ("other", "Other"),
        ],
        required=True,
        default="month_end",
        index=True,
    )

    # Optional: role routing by codes (directory)
    prep_by_code = fields.Char()
    review_by_code = fields.Char()
    approve_by_code = fields.Char()

    # Scheduling rules
    anchor = fields.Selection(
        [
            ("month_end", "Month End (last day)"),
            ("deadline", "Filing Deadline"),
            ("manual", "Manual"),
        ],
        default="month_end",
        required=True,
    )

    offset_days = fields.Integer(default=0, help="Days from anchor. Negative = before.")
    default_duration_days = fields.Integer(default=1)

    # Task meta
    task_category = fields.Selection(
        [
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
        ],
        default="other",
        index=True,
    )

    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "tmpl_name_unique",
            "unique(name, category)",
            "Template name must be unique per category.",
        ),
    ]

    @api.model
    def _upsert_from_seed(self, row: dict, strict: bool = False):
        name = (row or {}).get("name")
        category = (row or {}).get("category")
        if not name or not category:
            if strict:
                raise ValidationError(_("Seed template row missing name/category."))
            return False
        vals = {
            "sequence": int((row or {}).get("sequence", 10)),
            "task_category": (row or {}).get("task_category", "other"),
            "prep_by_code": (row or {}).get("prep_by_code"),
            "review_by_code": (row or {}).get("review_by_code"),
            "approve_by_code": (row or {}).get("approve_by_code"),
            "anchor": (row or {}).get("anchor", "month_end"),
            "offset_days": int((row or {}).get("offset_days", 0)),
            "default_duration_days": int((row or {}).get("default_duration_days", 1)),
            "active": bool((row or {}).get("active", True)),
        }
        rec = self.search([("name", "=", name), ("category", "=", category)], limit=1)
        if rec:
            rec.write(vals)
            return rec
        vals.update({"name": name, "category": category})
        return self.create(vals)
