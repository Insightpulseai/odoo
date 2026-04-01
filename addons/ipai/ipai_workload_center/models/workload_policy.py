from odoo import fields, models


class IpaiWorkloadPolicyCheck(models.Model):
    _name = "ipai.workload.policy.check"
    _description = "Workload Policy Check"
    _rec_name = "check_key"
    _order = "last_checked_at desc"

    workload_id = fields.Many2one(
        "ipai.workload", required=True, ondelete="cascade"
    )
    environment_id = fields.Many2one(
        "ipai.workload.environment", ondelete="set null"
    )
    check_key = fields.Char(
        required=True,
        help="e.g. no-plaintext-secrets, backup-immutability, image-digest-parity",
    )
    severity = fields.Selection(
        [
            ("info", "Info"),
            ("warning", "Warning"),
            ("critical", "Critical"),
            ("blocker", "Blocker"),
        ],
        default="warning",
    )
    status = fields.Selection(
        [
            ("pass", "Pass"),
            ("fail", "Fail"),
            ("skip", "Skipped"),
            ("unknown", "Unknown"),
        ],
        default="unknown",
    )
    last_checked_at = fields.Datetime()
    details_json = fields.Text(help="Structured check details and remediation")
