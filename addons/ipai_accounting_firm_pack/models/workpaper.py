# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class Workpaper(models.Model):
    """Workpaper for accounting engagement documentation."""

    _name = "ipai.workpaper"
    _description = "IPAI Workpaper"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "engagement_id, sequence, name"

    name = fields.Char(string="Workpaper Name", required=True, tracking=True)
    reference = fields.Char(string="Reference Code", tracking=True)
    sequence = fields.Integer(string="Sequence", default=10)

    engagement_id = fields.Many2one(
        "ipai.engagement",
        string="Engagement",
        required=True,
        tracking=True,
        ondelete="cascade",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Client",
        related="engagement_id.partner_id",
        store=True,
    )

    workpaper_type = fields.Selection(
        [
            ("trial_balance", "Trial Balance"),
            ("lead_schedule", "Lead Schedule"),
            ("supporting_schedule", "Supporting Schedule"),
            ("reconciliation", "Reconciliation"),
            ("analytical_review", "Analytical Review"),
            ("testing", "Testing Documentation"),
            ("memo", "Memo"),
            ("correspondence", "Correspondence"),
            ("checklist", "Checklist"),
            ("other", "Other"),
        ],
        string="Workpaper Type",
        required=True,
        tracking=True,
    )

    account_area = fields.Selection(
        [
            ("cash", "Cash & Bank"),
            ("receivables", "Accounts Receivable"),
            ("inventory", "Inventory"),
            ("fixed_assets", "Fixed Assets"),
            ("payables", "Accounts Payable"),
            ("accruals", "Accruals"),
            ("debt", "Debt"),
            ("equity", "Equity"),
            ("revenue", "Revenue"),
            ("expenses", "Expenses"),
            ("payroll", "Payroll"),
            ("tax", "Tax"),
            ("general", "General"),
        ],
        string="Account Area",
        default="general",
    )

    signoff_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("prepared", "Prepared"),
            ("reviewed", "Reviewed"),
            ("approved", "Approved"),
        ],
        string="Signoff Status",
        default="draft",
        tracking=True,
    )

    prepared_by_id = fields.Many2one(
        "res.users",
        string="Prepared By",
        tracking=True,
    )

    prepared_date = fields.Date(string="Prepared Date")

    reviewed_by_id = fields.Many2one(
        "res.users",
        string="Reviewed By",
        tracking=True,
    )

    review_date = fields.Date(string="Review Date")

    approved_by_id = fields.Many2one(
        "res.users",
        string="Approved By",
        tracking=True,
    )

    approval_date = fields.Date(string="Approval Date")

    # File storage
    file = fields.Binary(string="Workpaper File", attachment=True)
    file_name = fields.Char(string="File Name")

    # Link to DMS if available
    dms_file_id = fields.Integer(
        string="DMS File ID",
        help="Reference to DMS file",
    )

    # Time tracking
    billable_hours = fields.Float(
        string="Billable Hours",
        tracking=True,
    )

    description = fields.Html(string="Description/Scope")
    conclusion = fields.Text(string="Conclusion")
    notes = fields.Text(string="Internal Notes")

    # Review notes
    review_notes = fields.Text(string="Review Notes")

    def action_mark_prepared(self):
        self.write(
            {
                "signoff_state": "prepared",
                "prepared_by_id": self.env.user.id,
                "prepared_date": fields.Date.today(),
            }
        )

    def action_mark_reviewed(self):
        self.write(
            {
                "signoff_state": "reviewed",
                "reviewed_by_id": self.env.user.id,
                "review_date": fields.Date.today(),
            }
        )

    def action_approve(self):
        self.write(
            {
                "signoff_state": "approved",
                "approved_by_id": self.env.user.id,
                "approval_date": fields.Date.today(),
            }
        )

    def action_reset_draft(self):
        self.write(
            {
                "signoff_state": "draft",
                "prepared_by_id": False,
                "prepared_date": False,
                "reviewed_by_id": False,
                "review_date": False,
                "approved_by_id": False,
                "approval_date": False,
            }
        )

    _sql_constraints = [
        (
            "engagement_reference_uniq",
            "unique(engagement_id, reference)",
            "Workpaper reference must be unique within an engagement!",
        ),
    ]
