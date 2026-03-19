# -*- coding: utf-8 -*-
import json

from odoo import _, api, fields, models


class ContentCalendarItem(models.Model):
    """Content calendar for campaign scheduling."""

    _name = "ipai.content.calendar.item"
    _description = "IPAI Content Calendar Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheduled_datetime"

    name = fields.Char(string="Post Title", required=True, tracking=True)

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

    asset_id = fields.Many2one(
        "ipai.asset",
        string="Asset",
    )

    channel = fields.Selection(
        [
            ("facebook", "Facebook"),
            ("instagram", "Instagram"),
            ("twitter", "Twitter/X"),
            ("linkedin", "LinkedIn"),
            ("tiktok", "TikTok"),
            ("youtube", "YouTube"),
            ("pinterest", "Pinterest"),
            ("website", "Website/Blog"),
            ("email", "Email"),
            ("other", "Other"),
        ],
        string="Channel",
        required=True,
        tracking=True,
    )

    post_type = fields.Selection(
        [
            ("organic", "Organic"),
            ("paid", "Paid/Sponsored"),
            ("story", "Story"),
            ("reel", "Reel/Short"),
            ("live", "Live"),
            ("carousel", "Carousel"),
            ("article", "Article/Blog"),
        ],
        string="Post Type",
        default="organic",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("scheduled", "Scheduled"),
            ("published", "Published"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    scheduled_datetime = fields.Datetime(
        string="Scheduled Date/Time",
        required=True,
        tracking=True,
    )

    published_datetime = fields.Datetime(string="Published Date/Time")

    copy = fields.Text(string="Post Copy")
    hashtags = fields.Char(string="Hashtags")
    link_url = fields.Char(string="Link URL")

    notes = fields.Text(string="Notes")

    # For calendar view
    start = fields.Datetime(
        string="Start",
        compute="_compute_calendar_fields",
        store=True,
    )

    @api.depends("scheduled_datetime")
    def _compute_calendar_fields(self):
        for item in self:
            item.start = item.scheduled_datetime

    def action_schedule(self):
        self.write({"state": "scheduled"})

    def action_publish(self):
        self.write(
            {
                "state": "published",
                "published_datetime": fields.Datetime.now(),
            }
        )

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset_draft(self):
        self.write({"state": "draft"})


class PerformanceSnapshot(models.Model):
    """Performance metrics snapshot for campaigns."""

    _name = "ipai.performance.snapshot"
    _description = "IPAI Campaign Performance Snapshot"
    _order = "date desc, campaign_id"

    campaign_id = fields.Many2one(
        "ipai.campaign",
        string="Campaign",
        required=True,
        ondelete="cascade",
    )

    brand_id = fields.Many2one(
        "ipai.client.brand",
        string="Brand",
        related="campaign_id.brand_id",
        store=True,
    )

    date = fields.Date(
        string="Snapshot Date",
        required=True,
        default=fields.Date.today,
    )

    channel = fields.Selection(
        [
            ("all", "All Channels"),
            ("facebook", "Facebook"),
            ("instagram", "Instagram"),
            ("twitter", "Twitter/X"),
            ("linkedin", "LinkedIn"),
            ("tiktok", "TikTok"),
            ("youtube", "YouTube"),
            ("google", "Google Ads"),
            ("other", "Other"),
        ],
        string="Channel",
        default="all",
    )

    # Core metrics
    reach = fields.Integer(string="Reach")
    impressions = fields.Integer(string="Impressions")
    clicks = fields.Integer(string="Clicks")
    engagement = fields.Integer(string="Engagements")

    # Calculated rates
    ctr = fields.Float(
        string="CTR (%)",
        compute="_compute_rates",
        store=True,
        digits=(16, 2),
    )
    engagement_rate = fields.Float(
        string="Engagement Rate (%)",
        compute="_compute_rates",
        store=True,
        digits=(16, 2),
    )

    # Conversion metrics
    leads = fields.Integer(string="Leads")
    conversions = fields.Integer(string="Conversions")

    # Cost metrics
    spend = fields.Monetary(
        string="Spend",
        currency_field="currency_id",
    )

    cpc = fields.Monetary(
        string="CPC",
        currency_field="currency_id",
        compute="_compute_costs",
        store=True,
    )

    cpm = fields.Monetary(
        string="CPM",
        currency_field="currency_id",
        compute="_compute_costs",
        store=True,
    )

    cpl = fields.Monetary(
        string="CPL",
        currency_field="currency_id",
        compute="_compute_costs",
        store=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    # Extended metrics (JSON for flexibility)
    metrics_json = fields.Text(
        string="Additional Metrics (JSON)",
        help="JSON object for additional platform-specific metrics",
        default="{}",
    )

    notes = fields.Text(string="Notes")

    @api.depends("clicks", "impressions", "engagement", "reach")
    def _compute_rates(self):
        for snapshot in self:
            snapshot.ctr = (
                (snapshot.clicks / snapshot.impressions * 100)
                if snapshot.impressions
                else 0
            )
            snapshot.engagement_rate = (
                (snapshot.engagement / snapshot.reach * 100) if snapshot.reach else 0
            )

    @api.depends("spend", "clicks", "impressions", "leads")
    def _compute_costs(self):
        for snapshot in self:
            snapshot.cpc = snapshot.spend / snapshot.clicks if snapshot.clicks else 0
            snapshot.cpm = (
                snapshot.spend / snapshot.impressions * 1000
                if snapshot.impressions
                else 0
            )
            snapshot.cpl = snapshot.spend / snapshot.leads if snapshot.leads else 0

    def get_metrics_dict(self):
        """Return extended metrics as Python dict."""
        self.ensure_one()
        try:
            return json.loads(self.metrics_json or "{}")
        except json.JSONDecodeError:
            return {}

    _sql_constraints = [
        (
            "campaign_date_channel_uniq",
            "unique(campaign_id, date, channel)",
            "Only one snapshot per campaign/date/channel combination!",
        ),
    ]
