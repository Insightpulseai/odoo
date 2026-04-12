"""PPM OKR Objective — strategic objective with computed health.

Delta model: OKR tracking is not available in CE or OCA project modules.
Replaces the monolithic HTML dashboard with native Odoo model + views.
"""

from odoo import api, fields, models


class PPMOKRObjective(models.Model):
    _name = "ppm.okr.objective"
    _description = "PPM OKR Objective"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, code"
    _rec_name = "display_name"

    code = fields.Char(
        string="Code",
        required=True,
        tracking=True,
        help="e.g. O1, O2, O3",
    )
    name = fields.Char(
        string="Objective",
        required=True,
        tracking=True,
    )
    display_name = fields.Char(
        compute="_compute_display_name",
        store=True,
    )
    description = fields.Text(string="Description")
    sequence = fields.Integer(default=10)

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        tracking=True,
    )

    period_start = fields.Date(string="Period Start")
    period_end = fields.Date(string="Period End")
    review_cadence = fields.Selection(
        [
            ("weekly", "Weekly"),
            ("biweekly", "Bi-weekly"),
            ("monthly", "Monthly"),
        ],
        string="Review Cadence",
        default="monthly",
    )

    key_result_ids = fields.One2many(
        "ppm.okr.key_result",
        "objective_id",
        string="Key Results",
    )

    score = fields.Float(
        string="Score",
        digits=(3, 2),
        compute="_compute_score",
        store=True,
        help="0.0-1.0 average of KR scores. 0.7 = aspirational success.",
    )
    status = fields.Selection(
        [
            ("on_track", "On Track"),
            ("at_risk", "At Risk"),
            ("off_track", "Off Track"),
            ("blocked", "Blocked"),
        ],
        string="Status",
        compute="_compute_status",
        store=True,
        tracking=True,
    )
    color = fields.Integer(
        compute="_compute_color",
    )

    kr_count = fields.Integer(
        compute="_compute_kr_count",
    )
    sc_ph_refs = fields.Char(
        string="SC-PH References",
        help="Comma-separated SC-PH-* IDs from the PRD success criteria.",
    )

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.code} — {rec.name}" if rec.code else rec.name

    @api.depends("key_result_ids.score")
    def _compute_score(self):
        for rec in self:
            krs = rec.key_result_ids
            rec.score = sum(krs.mapped("score")) / len(krs) if krs else 0.0

    @api.depends("score", "key_result_ids.status")
    def _compute_status(self):
        for rec in self:
            kr_statuses = rec.key_result_ids.mapped("status")
            if "blocked" in kr_statuses:
                rec.status = "blocked"
            elif rec.score < 0.4:
                rec.status = "off_track"
            elif rec.score < 0.7:
                rec.status = "at_risk"
            else:
                rec.status = "on_track"

    def _compute_color(self):
        color_map = {"on_track": 10, "at_risk": 2, "off_track": 1, "blocked": 9}
        for rec in self:
            rec.color = color_map.get(rec.status, 0)

    def _compute_kr_count(self):
        for rec in self:
            rec.kr_count = len(rec.key_result_ids)

    _sql_constraints = [
        ("code_uniq", "UNIQUE(code, company_id)", "Objective code must be unique per company."),
    ]
