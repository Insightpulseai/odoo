"""IPAI Tax Intelligence — Tax Exception model.

Stores detected tax validation exceptions with full review state machine,
explainability fields, and audit log linkage.

Constitution Principle 3: Every Pulser tax decision must include rationale,
source inputs, confidence, and audit trace.
Constitution Principle 6: Draft-first — exceptions block posting until resolved.
"""

from odoo import api, fields, models


class TaxException(models.Model):
    _name = "tax.exception"
    _description = "Tax Exception"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "detected_date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("tax.exception") or "/",
        copy=False,
    )
    source_model = fields.Char(
        string="Source Model",
        required=True,
        help="Technical model name of the document that triggered this exception (e.g. account.move).",
    )
    source_id = fields.Integer(
        string="Source Record ID",
        required=True,
        help="ID of the source document record.",
    )
    rule_id = fields.Many2one(
        "tax.validation.rule",
        string="Triggered Rule",
        required=True,
        ondelete="restrict",
        index=True,
    )
    exception_type = fields.Selection(
        [
            ("rate_mismatch", "Rate Mismatch"),
            ("missing_tax", "Missing Tax"),
            ("wrong_jurisdiction", "Wrong Jurisdiction"),
            ("missing_document", "Missing Document"),
            ("withholding_error", "Withholding Error"),
            ("other", "Other"),
        ],
        string="Exception Type",
        required=True,
        default="other",
    )
    state = fields.Selection(
        [
            ("detected", "Detected"),
            ("under_review", "Under Review"),
            ("resolved", "Resolved"),
            ("waived", "Waived"),
            ("escalated", "Escalated"),
        ],
        string="Status",
        required=True,
        default="detected",
        tracking=True,
    )
    severity = fields.Selection(
        related="rule_id.severity",
        string="Severity",
        store=True,
        readonly=True,
    )
    detected_date = fields.Datetime(
        string="Detected At",
        required=True,
        default=fields.Datetime.now,
        readonly=True,
    )
    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer",
        readonly=True,
        tracking=True,
    )
    review_date = fields.Datetime(
        string="Reviewed At",
        readonly=True,
    )
    resolution = fields.Text(
        string="Resolution Notes",
        help="Human-entered notes describing how this exception was resolved or waived.",
    )

    # Explainability fields (Constitution Principle 3)
    rationale = fields.Text(
        string="Rationale",
        help="Why this exception was detected — machine-generated or manually entered.",
    )
    inputs_summary = fields.Text(
        string="Inputs Summary",
        help="Summary of the source data inputs that informed this exception.",
    )
    confidence = fields.Float(
        string="Confidence",
        digits=(4, 2),
        default=0.0,
        help="Confidence score (0.0 – 1.0) from the validation engine.",
    )
    policy_reference = fields.Char(
        string="Policy Reference",
        related="rule_id.policy_reference",
        store=True,
        readonly=True,
        help="BIR RR, NIRC section, or internal policy identifier.",
    )

    audit_log_ids = fields.One2many(
        "tax.audit.log",
        "exception_id",
        string="Audit Log",
        readonly=True,
    )
    audit_log_count = fields.Integer(
        string="Audit Log Entries",
        compute="_compute_audit_log_count",
    )

    @api.depends("audit_log_ids")
    def _compute_audit_log_count(self):
        for rec in self:
            rec.audit_log_count = len(rec.audit_log_ids)

    # ---------------------------------------------------------------
    # State machine actions
    # ---------------------------------------------------------------

    def action_start_review(self):
        """Move exception to under_review and assign reviewer."""
        for exc in self:
            exc._transition_state("under_review", "review_started")
            exc.write({
                "reviewer_id": self.env.uid,
            })

    def action_resolve(self):
        """Mark exception as resolved."""
        for exc in self:
            exc._transition_state("resolved", "resolved")
            exc.write({
                "reviewer_id": self.env.uid,
                "review_date": fields.Datetime.now(),
            })

    def action_waive(self):
        """Waive exception — acknowledged and accepted."""
        for exc in self:
            exc._transition_state("waived", "waived")
            exc.write({
                "reviewer_id": self.env.uid,
                "review_date": fields.Datetime.now(),
            })

    def action_escalate(self):
        """Escalate exception for management review."""
        for exc in self:
            exc._transition_state("escalated", "escalated")

    def action_reopen(self):
        """Reopen a resolved/waived exception."""
        for exc in self:
            exc._transition_state("detected", "reopened")
            exc.write({
                "reviewer_id": False,
                "review_date": False,
            })

    def _transition_state(self, new_state, action):
        """Execute a state transition and log to audit trail."""
        self.ensure_one()
        old_state = self.state
        self.write({"state": new_state})
        self.env["tax.audit.log"].create({
            "exception_id": self.id,
            "user_id": self.env.uid,
            "action": action,
            "old_state": old_state,
            "new_state": new_state,
        })

    def action_view_audit_logs(self):
        """Open audit log entries for this exception."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Audit Log",
            "res_model": "tax.audit.log",
            "domain": [("exception_id", "=", self.id)],
            "view_mode": "list",
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("tax.exception") or "/"
                )
        records = super().create(vals_list)
        for rec in records:
            self.env["tax.audit.log"].create({
                "exception_id": rec.id,
                "user_id": self.env.uid,
                "action": "created",
                "old_state": False,
                "new_state": rec.state,
                "notes": f"Exception created for rule: {rec.rule_id.name}",
            })
        return records
