# -*- coding: utf-8 -*-
# Copyright (C) InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    ces_campaign_id = fields.Char(
        string="CES Campaign ID",
        help="External CES campaign identifier.",
        index=True,
        copy=False,
    )
    ces_brand = fields.Char(
        string="Brand (CES)",
        help="Brand code as used in CES.",
        index=True,
    )
    ces_client = fields.Char(
        string="Client (CES)",
        help="Top-level client name for LIONS / CES reporting.",
    )
    ces_agency = fields.Selection(
        [
            ("tbwa", "TBWA"),
            ("tbwa_santiago_mangada_puno", "TBWA\\Santiago Mangada Puno"),
            ("fleishmanhillard", "FleishmanHillard"),
            ("ddb", "DDB"),
            ("other", "Other"),
        ],
        string="Agency",
        default="tbwa",
        help="Agency handling this campaign.",
    )
    ces_media_mix = fields.Char(
        string="Media Mix",
        help="Comma-separated list of media channels (TV, OOH, Digital, etc.).",
    )
    ces_media_channels = fields.Many2many(
        "ces.media.channel",
        string="Media Channels",
        help="Media channels used in this campaign.",
    )
    ces_is_flagship = fields.Boolean(
        string="Flagship Campaign",
        help="Indicates TBWA flagship campaigns for CES dashboards.",
    )
    ces_is_awards_entry = fields.Boolean(
        string="Awards Entry",
        help="Mark campaigns entered for awards (Cannes, Spikes, etc.).",
    )
    ces_campaign_type = fields.Selection(
        [
            ("brand", "Brand Campaign"),
            ("product_launch", "Product Launch"),
            ("promo", "Promotional"),
            ("seasonal", "Seasonal"),
            ("always_on", "Always On"),
            ("crisis", "Crisis/PR"),
            ("event", "Event"),
            ("social", "Social Campaign"),
            ("other", "Other"),
        ],
        string="Campaign Type",
        help="Classification of campaign type for CES analytics.",
    )
    ces_start_date = fields.Date(
        string="Campaign Start",
        help="Campaign flight start date.",
    )
    ces_end_date = fields.Date(
        string="Campaign End",
        help="Campaign flight end date.",
    )
    ces_budget_total = fields.Monetary(
        string="Total Budget",
        currency_field="currency_id",
        help="Total campaign budget for CES reporting.",
    )
    ces_production_budget = fields.Monetary(
        string="Production Budget",
        currency_field="currency_id",
        help="Production costs budget.",
    )
    ces_media_budget = fields.Monetary(
        string="Media Budget",
        currency_field="currency_id",
        help="Media placement budget.",
    )
    ces_fee_budget = fields.Monetary(
        string="Agency Fees Budget",
        currency_field="currency_id",
        help="Agency fees budget.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )
    ces_kpi_reach = fields.Float(
        string="Target Reach",
        help="Target reach/impressions for the campaign.",
    )
    ces_kpi_engagement = fields.Float(
        string="Target Engagement",
        help="Target engagement rate.",
    )
    ces_notes = fields.Html(
        string="Campaign Notes",
        help="Internal notes about the campaign.",
    )

    _sql_constraints = [
        (
            "ces_campaign_id_unique",
            "UNIQUE(ces_campaign_id)",
            "CES Campaign ID must be unique.",
        ),
    ]

    @api.model
    def _generate_ces_campaign_id(self, brand, year=None):
        """Generate a unique CES campaign ID."""
        from datetime import date
        year = year or date.today().year
        brand_code = (brand or "XX")[:4].upper()
        sequence = self.env["ir.sequence"].next_by_code("ces.campaign.id") or "0001"
        return f"CES-{year}-{brand_code}-{sequence}"


class CesMediaChannel(models.Model):
    _name = "ces.media.channel"
    _description = "CES Media Channel"
    _order = "sequence, name"

    name = fields.Char(string="Channel Name", required=True)
    code = fields.Char(string="Code", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(default=True)
    description = fields.Text(string="Description")
    channel_type = fields.Selection(
        [
            ("traditional", "Traditional"),
            ("digital", "Digital"),
            ("experiential", "Experiential"),
        ],
        string="Channel Type",
        default="traditional",
    )

    _sql_constraints = [
        ("code_unique", "UNIQUE(code)", "Channel code must be unique."),
    ]
