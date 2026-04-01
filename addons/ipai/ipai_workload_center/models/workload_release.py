from odoo import fields, models


class IpaiWorkloadRelease(models.Model):
    _name = "ipai.workload.release"
    _description = "Workload Release"
    _inherit = ["mail.thread"]
    _rec_name = "release_key"
    _order = "deployed_at desc"

    workload_id = fields.Many2one(
        "ipai.workload", required=True, ondelete="cascade", tracking=True
    )
    environment_id = fields.Many2one(
        "ipai.workload.environment", ondelete="set null", tracking=True
    )
    release_key = fields.Char(required=True, tracking=True)
    version_label = fields.Char(tracking=True)
    artifact_ref = fields.Char(
        help="Image digest or artifact URL (e.g. acr/repo@sha256:...)"
    )
    deployed_at = fields.Datetime(tracking=True)
    deployed_by = fields.Many2one("res.users")
    rollback_ref = fields.Char(help="Previous artifact ref for rollback")
    status = fields.Selection(
        [
            ("pending", "Pending"),
            ("deployed", "Deployed"),
            ("validated", "Validated"),
            ("failed", "Failed"),
            ("rolled_back", "Rolled Back"),
        ],
        default="pending",
        tracking=True,
    )

    validation_run_ids = fields.One2many(
        "ipai.workload.validation.run", "release_id", string="Validation Runs"
    )
    evidence_ids = fields.One2many(
        "ipai.workload.evidence", "release_id", string="Evidence"
    )
