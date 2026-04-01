from odoo import fields, models


class IpaiWorkloadEvidence(models.Model):
    _name = "ipai.workload.evidence"
    _description = "Workload Evidence"
    _rec_name = "name"
    _order = "captured_at desc"

    workload_id = fields.Many2one(
        "ipai.workload", required=True, ondelete="cascade"
    )
    environment_id = fields.Many2one(
        "ipai.workload.environment", ondelete="set null"
    )
    release_id = fields.Many2one(
        "ipai.workload.release", ondelete="set null"
    )
    validation_run_id = fields.Many2one(
        "ipai.workload.validation.run", ondelete="set null"
    )
    name = fields.Char(required=True)
    evidence_type = fields.Selection(
        [
            ("report", "Report"),
            ("log", "Log"),
            ("screenshot", "Screenshot"),
            ("export", "Export"),
            ("json", "JSON"),
        ],
        required=True,
    )
    attachment_id = fields.Many2one("ir.attachment", ondelete="set null")
    url = fields.Char(help="External evidence URL (e.g. docs/evidence/ path)")
    checksum = fields.Char(help="SHA-256 checksum of evidence artifact")
    captured_at = fields.Datetime()
