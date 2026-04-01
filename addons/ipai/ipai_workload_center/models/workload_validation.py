from odoo import fields, models


class IpaiWorkloadValidationRun(models.Model):
    _name = "ipai.workload.validation.run"
    _description = "Workload Validation Run"
    _inherit = ["mail.thread"]
    _rec_name = "display_name"
    _order = "started_at desc"

    workload_id = fields.Many2one(
        "ipai.workload", required=True, ondelete="cascade"
    )
    environment_id = fields.Many2one(
        "ipai.workload.environment", ondelete="set null"
    )
    release_id = fields.Many2one(
        "ipai.workload.release", ondelete="set null"
    )
    validation_type = fields.Selection(
        [
            ("smoke", "Smoke Test"),
            ("contract", "Contract Check"),
            ("policy", "Policy Check"),
            ("ha", "HA Validation"),
            ("recovery", "Recovery Validation"),
            ("full", "Full Suite"),
        ],
        required=True,
        tracking=True,
    )
    status = fields.Selection(
        [
            ("pending", "Pending"),
            ("running", "Running"),
            ("passed", "Passed"),
            ("failed", "Failed"),
            ("error", "Error"),
        ],
        default="pending",
        tracking=True,
    )
    started_at = fields.Datetime()
    finished_at = fields.Datetime()
    summary_json = fields.Text(help="Structured validation results")
    evidence_count = fields.Integer(
        compute="_compute_evidence_count"
    )

    evidence_ids = fields.One2many(
        "ipai.workload.evidence", "validation_run_id", string="Evidence"
    )

    display_name = fields.Char(compute="_compute_display_name", store=True)

    def _compute_evidence_count(self):
        for rec in self:
            rec.evidence_count = len(rec.evidence_ids)

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f"{rec.workload_id.key or ''}/{rec.validation_type or ''}"
                f" @ {rec.started_at or 'pending'}"
            )
