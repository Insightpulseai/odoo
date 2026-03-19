from odoo import fields, models


class PhHoliday(models.Model):
    """Philippine Holiday Calendar for workday calculations."""

    _name = "ipai.ph.holiday"
    _description = "Philippine Holiday"
    _order = "date"

    name = fields.Char(required=True, string="Holiday Name")
    date = fields.Date(required=True, index=True)
    holiday_type = fields.Selection(
        [
            ("regular", "Regular Holiday"),
            ("special", "Special Non-Working Holiday"),
            ("additional_special", "Additional Special Non-Working Holiday"),
        ],
        default="regular",
        required=True,
    )
    year = fields.Integer(compute="_compute_year", store=True)

    _sql_constraints = [
        ("date_unique", "UNIQUE(date)", "Holiday already exists for this date!"),
    ]

    def _compute_year(self):
        for rec in self:
            rec.year = rec.date.year if rec.date else False
