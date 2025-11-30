# ipai_ppm_demo/models/ppm_intake_request.py
from odoo import fields, models


class PpmIntakeRequest(models.Model):
    _name = "ppm.intake.request"
    _description = "PPM Project Intake Request"

    name = fields.Char(required=True)
    request_id = fields.Char()
    business_value_score = fields.Integer()
    ease_of_implementation = fields.Integer()
    strategic_alignment_score = fields.Integer()
    approval_stage = fields.Selection(
        [
            ("screening", "Screening"),
            ("approved", "Approved"),
            ("backlog", "Backlog"),
        ],
        default="screening",
    )
    status = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("approved", "Approved"),
            ("in_work", "In Work"),
        ],
        default="proposed",
    )
