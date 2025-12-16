# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ClientBrand(models.Model):
    """Client brand for marketing agency operations."""
    _name = "ipai.client.brand"
    _description = "IPAI Client Brand"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "partner_id, name"

    name = fields.Char(string="Brand Name", required=True, tracking=True)
    code = fields.Char(string="Brand Code", tracking=True)
    active = fields.Boolean(default=True)

    partner_id = fields.Many2one(
        "res.partner",
        string="Client",
        required=True,
        tracking=True,
        domain="[('is_company', '=', True)]",
    )

    brand_guidelines_url = fields.Char(
        string="Brand Guidelines URL",
        help="Link to brand guidelines document or folder",
    )

    logo = fields.Binary(string="Brand Logo", attachment=True)
    logo_filename = fields.Char(string="Logo Filename")

    tone_tags = fields.Char(
        string="Tone Tags",
        help="Comma-separated tone descriptors (e.g., professional, playful, bold)",
    )

    primary_color = fields.Char(string="Primary Color (Hex)")
    secondary_color = fields.Char(string="Secondary Color (Hex)")

    description = fields.Html(string="Brand Description")

    target_audience = fields.Text(
        string="Target Audience",
        help="Description of primary target audience segments",
    )

    brand_voice = fields.Text(
        string="Brand Voice",
        help="Guidelines for brand voice and messaging",
    )

    # Related records
    campaign_ids = fields.One2many(
        "ipai.campaign",
        "brand_id",
        string="Campaigns",
    )

    asset_ids = fields.One2many(
        "ipai.asset",
        "brand_id",
        string="Assets",
    )

    # Computed fields
    campaign_count = fields.Integer(
        string="Campaigns",
        compute="_compute_counts",
        store=True,
    )
    asset_count = fields.Integer(
        string="Assets",
        compute="_compute_counts",
        store=True,
    )

    @api.depends("campaign_ids", "asset_ids")
    def _compute_counts(self):
        for brand in self:
            brand.campaign_count = len(brand.campaign_ids)
            brand.asset_count = len(brand.asset_ids)

    def action_view_campaigns(self):
        """Open campaigns for this brand."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Campaigns"),
            "res_model": "ipai.campaign",
            "view_mode": "list,form,kanban",
            "domain": [("brand_id", "=", self.id)],
            "context": {"default_brand_id": self.id},
        }

    def action_view_assets(self):
        """Open assets for this brand."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Assets"),
            "res_model": "ipai.asset",
            "view_mode": "list,form,kanban",
            "domain": [("brand_id", "=", self.id)],
            "context": {"default_brand_id": self.id},
        }

    _sql_constraints = [
        ("partner_code_uniq", "unique(partner_id, code)", "Brand code must be unique per client!"),
    ]
