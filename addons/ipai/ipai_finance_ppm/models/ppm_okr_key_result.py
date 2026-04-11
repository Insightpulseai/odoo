"""PPM OKR Key Result — measurable outcome with target/actual/score.

Delta model: KR tracking with 0.0-1.0 scoring is not available in CE or OCA.
Each KR maps to a SC-PH-* success criterion from the Pulser PRD.
"""

from odoo import api, fields, models


class PPMOKRKeyResult(models.Model):
    _name = "ppm.okr.key_result"
    _description = "PPM OKR Key Result"
    _inherit = ["mail.thread"]
    _order = "objective_id, sequence, code"
    _rec_name = "display_name"

    code = fields.Char(
        string="Code",
        required=True,
        help="e.g. KR1, KR2, KR3 (unique per objective)",
    )
    name = fields.Char(
        string="Key Result",
        required=True,
    )
    display_name = fields.Char(
        compute="_compute_display_name",
        store=True,
    )
    sequence = fields.Integer(default=10)

    objective_id = fields.Many2one(
        "ppm.okr.objective",
        string="Objective",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        related="objective_id.company_id",
        store=True,
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        tracking=True,
    )

    # Measurement
    metric_source = fields.Char(
        string="Metric Source",
        help="SC-PH-* reference or measurement description.",
    )
    unit = fields.Char(
        string="Unit",
        help="minutes, %, count, currency, boolean",
    )
    baseline = fields.Float(string="Baseline", digits=(12, 2))
    target = fields.Float(string="Target", digits=(12, 2))
    current = fields.Float(
        string="Current",
        digits=(12, 2),
        tracking=True,
    )
    target_direction = fields.Selection(
        [
            ("higher_is_better", "Higher is Better"),
            ("lower_is_better", "Lower is Better"),
            ("exact", "Exact Match"),
        ],
        string="Direction",
        default="higher_is_better",
    )

    # Computed scoring
    score = fields.Float(
        string="Score",
        digits=(3, 2),
        compute="_compute_score",
        store=True,
        help="0.0-1.0. Score >= 0.7 = aspirational success.",
    )
    progress = fields.Float(
        string="Progress %",
        compute="_compute_score",
        store=True,
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
    trend = fields.Selection(
        [
            ("improving", "Improving"),
            ("stable", "Stable"),
            ("declining", "Declining"),
        ],
        string="Trend",
        default="stable",
    )
    color = fields.Integer(compute="_compute_color")

    last_measured = fields.Datetime(string="Last Measured")
    escalation_path = fields.Text(string="Escalation Path")
    notes = fields.Text(string="Notes")

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.code} — {rec.name}" if rec.code else rec.name

    @api.depends("baseline", "target", "current", "target_direction")
    def _compute_score(self):
        for rec in self:
            if not rec.target and rec.target != 0:
                rec.score = 0.0
                rec.progress = 0.0
                continue

            if rec.target_direction == "lower_is_better":
                # Lower is better: score = 1.0 when current <= target
                if rec.baseline == rec.target:
                    rec.score = 1.0 if rec.current <= rec.target else 0.0
                else:
                    range_val = rec.baseline - rec.target
                    if range_val <= 0:
                        rec.score = 1.0 if rec.current <= rec.target else 0.0
                    else:
                        raw = (rec.baseline - rec.current) / range_val
                        rec.score = max(0.0, min(1.0, raw))
            elif rec.target_direction == "exact":
                rec.score = 1.0 if rec.current == rec.target else 0.0
            else:
                # Higher is better (default)
                if rec.target == rec.baseline:
                    rec.score = 1.0 if rec.current >= rec.target else 0.0
                else:
                    range_val = rec.target - rec.baseline
                    if range_val <= 0:
                        rec.score = 1.0 if rec.current >= rec.target else 0.0
                    else:
                        raw = (rec.current - rec.baseline) / range_val
                        rec.score = max(0.0, min(1.0, raw))

            rec.progress = rec.score * 100

    @api.depends("score")
    def _compute_status(self):
        for rec in self:
            if rec.score >= 0.7:
                rec.status = "on_track"
            elif rec.score >= 0.4:
                rec.status = "at_risk"
            else:
                rec.status = "off_track"

    def _compute_color(self):
        color_map = {"on_track": 10, "at_risk": 2, "off_track": 1, "blocked": 9}
        for rec in self:
            rec.color = color_map.get(rec.status, 0)

    _sql_constraints = [
        (
            "code_objective_uniq",
            "UNIQUE(code, objective_id)",
            "KR code must be unique per objective.",
        ),
    ]
