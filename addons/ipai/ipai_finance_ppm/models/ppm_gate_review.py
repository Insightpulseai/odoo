"""PPM Gate Review — phase-gate governance for projects.

Delta model: stage-gate review objects are not in CE or OCA.
OCA `project_reviewer` provides task-level review, not project phase gates.
"""

from odoo import api, fields, models


class PPMGateReview(models.Model):
    _name = "ppm.gate.review"
    _description = "PPM Gate Review"
    _inherit = ["mail.thread"]
    _order = "gate_date desc"

    name = fields.Char(string="Gate Name", required=True)
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        related="project_id.company_id",
        store=True,
    )
    gate_type = fields.Selection(
        [
            ("initiation", "Initiation Gate"),
            ("planning", "Planning Gate"),
            ("execution", "Execution Gate"),
            ("monitoring", "Monitoring Gate"),
            ("closure", "Closure Gate"),
        ],
        string="Gate Type",
        required=True,
    )
    gate_date = fields.Date(string="Gate Date", required=True)
    reviewer_ids = fields.Many2many(
        "res.users",
        string="Reviewers",
    )
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("in_progress", "In Progress"),
            ("passed", "Passed"),
            ("conditional", "Conditional Pass"),
            ("failed", "Failed"),
            ("deferred", "Deferred"),
        ],
        string="Outcome",
        default="scheduled",
        tracking=True,
    )
    criteria = fields.Text(
        string="Gate Criteria",
        help="What must be true for this gate to pass",
    )
    findings = fields.Text(string="Findings")
    conditions = fields.Text(
        string="Conditions",
        help="Conditions that must be met for a conditional pass",
    )
    decision_date = fields.Date(string="Decision Date")
    decided_by_id = fields.Many2one("res.users", string="Decided By")

    def action_pass(self):
        self.ensure_one()
        self.write({
            "state": "passed",
            "decision_date": fields.Date.today(),
            "decided_by_id": self.env.uid,
        })
        self.message_post(body=f"Gate passed by {self.env.user.name}.")

    def action_conditional_pass(self):
        self.ensure_one()
        self.write({
            "state": "conditional",
            "decision_date": fields.Date.today(),
            "decided_by_id": self.env.uid,
        })
        self.message_post(
            body=f"Conditional pass by {self.env.user.name}. "
                 f"Conditions: {self.conditions or 'See gate record'}",
        )

    def action_fail(self):
        self.ensure_one()
        self.write({
            "state": "failed",
            "decision_date": fields.Date.today(),
            "decided_by_id": self.env.uid,
        })
        self.message_post(body=f"Gate failed by {self.env.user.name}.")
