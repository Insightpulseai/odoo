# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CreativeBrief(models.Model):
    """Creative brief for campaign production."""
    _name = "ipai.creative.brief"
    _description = "IPAI Creative Brief"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        string="Brief Title",
        required=True,
        tracking=True,
        default=lambda self: _("New Brief"),
    )

    campaign_id = fields.Many2one(
        "ipai.campaign",
        string="Campaign",
        required=True,
        tracking=True,
    )

    brand_id = fields.Many2one(
        "ipai.client.brand",
        string="Brand",
        related="campaign_id.brand_id",
        store=True,
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("review", "In Review"),
        ("approved", "Approved"),
        ("revision", "Needs Revision"),
        ("rejected", "Rejected"),
    ], string="Status", default="draft", tracking=True)

    # Brief content
    audience = fields.Text(
        string="Target Audience",
        help="Who is this creative targeting?",
    )

    single_minded_proposition = fields.Text(
        string="Single-Minded Proposition",
        help="The one key message or takeaway",
    )

    mandatories = fields.Text(
        string="Mandatories (JSON)",
        help="JSON list of mandatory elements to include",
        default='[]',
    )

    channels = fields.Text(
        string="Channels (JSON)",
        help="JSON list of channels for distribution",
        default='["social", "web"]',
    )

    tone = fields.Char(
        string="Tone",
        help="Desired tone for the creative",
    )

    key_messages = fields.Text(
        string="Key Messages",
        help="Primary messages to communicate",
    )

    call_to_action = fields.Char(string="Call to Action")

    deliverables_description = fields.Html(string="Deliverables Description")

    deadline = fields.Date(string="Creative Deadline", tracking=True)

    # Related assets
    asset_ids = fields.One2many(
        "ipai.asset",
        "brief_id",
        string="Assets",
    )

    asset_count = fields.Integer(compute="_compute_asset_count", store=True)

    @api.depends("asset_ids")
    def _compute_asset_count(self):
        for brief in self:
            brief.asset_count = len(brief.asset_ids)

    def action_submit_review(self):
        self.write({"state": "review"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_request_revision(self):
        self.write({"state": "revision"})

    def action_reject(self):
        self.write({"state": "rejected"})

    def action_reset_draft(self):
        self.write({"state": "draft"})


class Asset(models.Model):
    """Creative asset for campaigns."""
    _name = "ipai.asset"
    _description = "IPAI Creative Asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Asset Name", required=True, tracking=True)
    code = fields.Char(string="Asset Code")

    campaign_id = fields.Many2one(
        "ipai.campaign",
        string="Campaign",
        tracking=True,
    )

    brand_id = fields.Many2one(
        "ipai.client.brand",
        string="Brand",
        required=True,
        tracking=True,
    )

    brief_id = fields.Many2one(
        "ipai.creative.brief",
        string="Creative Brief",
    )

    asset_type = fields.Selection([
        ("video", "Video"),
        ("image", "Image/Static"),
        ("copy", "Copy/Text"),
        ("deck", "Presentation/Deck"),
        ("audio", "Audio"),
        ("animation", "Animation/GIF"),
        ("document", "Document"),
        ("other", "Other"),
    ], string="Asset Type", required=True, default="image", tracking=True)

    version = fields.Integer(string="Version", default=1, tracking=True)

    state = fields.Selection([
        ("draft", "Draft"),
        ("internal_review", "Internal Review"),
        ("client_review", "Client Review"),
        ("approved", "Approved"),
        ("revision", "Revision Needed"),
        ("rejected", "Rejected"),
        ("published", "Published"),
    ], string="Status", default="draft", tracking=True)

    # File storage
    file = fields.Binary(string="File", attachment=True)
    file_name = fields.Char(string="File Name")
    file_size = fields.Integer(string="File Size (KB)")
    file_url = fields.Char(string="File URL", help="External URL if hosted elsewhere")

    # Specifications
    format = fields.Char(string="Format", help="e.g., 1080x1080, 16:9, etc.")
    duration = fields.Float(string="Duration (seconds)", help="For video/audio")
    file_type = fields.Char(string="File Type", help="e.g., MP4, PNG, DOCX")

    description = fields.Text(string="Description")
    notes = fields.Text(string="Internal Notes")

    # Approval workflow
    approval_cycle_ids = fields.One2many(
        "ipai.approval.cycle",
        "asset_id",
        string="Approval History",
    )

    def action_submit_internal(self):
        self.write({"state": "internal_review"})

    def action_submit_client(self):
        self.write({"state": "client_review"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_request_revision(self):
        self.write({"state": "revision"})
        # Increment version when revision is requested
        self.write({"version": self.version + 1})

    def action_reject(self):
        self.write({"state": "rejected"})

    def action_publish(self):
        self.write({"state": "published"})

    def action_reset_draft(self):
        self.write({"state": "draft"})


class ApprovalCycle(models.Model):
    """Approval workflow for assets."""
    _name = "ipai.approval.cycle"
    _description = "IPAI Asset Approval Cycle"
    _order = "create_date desc"

    asset_id = fields.Many2one(
        "ipai.asset",
        string="Asset",
        required=True,
        ondelete="cascade",
    )

    stage = fields.Selection([
        ("internal", "Internal Review"),
        ("client", "Client Review"),
        ("legal", "Legal Review"),
        ("final", "Final Approval"),
    ], string="Review Stage", required=True)

    approver_id = fields.Many2one(
        "res.partner",
        string="Approver",
        required=True,
    )

    user_id = fields.Many2one(
        "res.users",
        string="Reviewed By",
        help="User who recorded this decision",
        default=lambda self: self.env.user,
    )

    due_date = fields.Date(string="Due Date")
    decision_date = fields.Datetime(string="Decision Date")

    decision = fields.Selection([
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("revision", "Revision Needed"),
        ("rejected", "Rejected"),
    ], string="Decision", default="pending", required=True)

    comments = fields.Text(string="Comments")
    revision_notes = fields.Text(string="Revision Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("decision") and vals["decision"] != "pending":
                vals["decision_date"] = fields.Datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        if "decision" in vals and vals["decision"] != "pending":
            vals["decision_date"] = fields.Datetime.now()
        return super().write(vals)
