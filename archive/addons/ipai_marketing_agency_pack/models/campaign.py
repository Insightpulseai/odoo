# -*- coding: utf-8 -*-
import json

from odoo.exceptions import ValidationError

from odoo import _, api, fields, models


class Campaign(models.Model):
    """Marketing campaign management."""

    _name = "ipai.campaign"
    _description = "IPAI Marketing Campaign"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_date desc, name"

    name = fields.Char(string="Campaign Name", required=True, tracking=True)
    code = fields.Char(string="Campaign Code", tracking=True)
    active = fields.Boolean(default=True)

    brand_id = fields.Many2one(
        "ipai.client.brand",
        string="Brand",
        required=True,
        tracking=True,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Client",
        related="brand_id.partner_id",
        store=True,
    )

    project_id = fields.Many2one(
        "project.project",
        string="Delivery Project",
        tracking=True,
    )

    objective = fields.Selection(
        [
            ("awareness", "Brand Awareness"),
            ("consideration", "Consideration"),
            ("conversion", "Conversion"),
            ("retention", "Retention/Loyalty"),
            ("engagement", "Engagement"),
            ("launch", "Product Launch"),
        ],
        string="Objective",
        required=True,
        tracking=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("planning", "Planning"),
            ("briefing", "Briefing"),
            ("production", "Production"),
            ("live", "Live"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    start_date = fields.Date(string="Start Date", required=True, tracking=True)
    end_date = fields.Date(string="End Date", required=True, tracking=True)

    budget = fields.Monetary(
        string="Budget",
        currency_field="currency_id",
        tracking=True,
    )

    spent = fields.Monetary(
        string="Spent",
        currency_field="currency_id",
        compute="_compute_financials",
        store=True,
    )

    remaining_budget = fields.Monetary(
        string="Remaining",
        currency_field="currency_id",
        compute="_compute_financials",
        store=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    kpi_targets = fields.Text(
        string="KPI Targets (JSON)",
        help="JSON structure for key performance indicator targets",
        default='{"reach": 0, "impressions": 0, "clicks": 0, "leads": 0, "conversions": 0}',
    )

    description = fields.Html(string="Campaign Description")

    # Related records
    brief_ids = fields.One2many(
        "ipai.creative.brief",
        "campaign_id",
        string="Creative Briefs",
    )

    asset_ids = fields.One2many(
        "ipai.asset",
        "campaign_id",
        string="Assets",
    )

    calendar_item_ids = fields.One2many(
        "ipai.content.calendar.item",
        "campaign_id",
        string="Content Calendar",
    )

    snapshot_ids = fields.One2many(
        "ipai.performance.snapshot",
        "campaign_id",
        string="Performance Snapshots",
    )

    # Computed counts
    brief_count = fields.Integer(compute="_compute_counts", store=True)
    asset_count = fields.Integer(compute="_compute_counts", store=True)
    calendar_count = fields.Integer(compute="_compute_counts", store=True)

    @api.depends("brief_ids", "asset_ids", "calendar_item_ids")
    def _compute_counts(self):
        for campaign in self:
            campaign.brief_count = len(campaign.brief_ids)
            campaign.asset_count = len(campaign.asset_ids)
            campaign.calendar_count = len(campaign.calendar_item_ids)

    @api.depends("budget", "snapshot_ids.spend")
    def _compute_financials(self):
        for campaign in self:
            campaign.spent = sum(campaign.snapshot_ids.mapped("spend"))
            campaign.remaining_budget = (campaign.budget or 0) - campaign.spent

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for campaign in self:
            if campaign.end_date and campaign.start_date:
                if campaign.end_date < campaign.start_date:
                    raise ValidationError(_("End date must be after start date."))

    def action_start_planning(self):
        self.write({"state": "planning"})

    def action_start_briefing(self):
        self.write({"state": "briefing"})

    def action_start_production(self):
        self.write({"state": "production"})

    def action_go_live(self):
        self.write({"state": "live"})

    def action_complete(self):
        self.write({"state": "completed"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_view_briefs(self):
        """Open creative briefs for this campaign."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Creative Briefs"),
            "res_model": "ipai.creative.brief",
            "view_mode": "list,form",
            "domain": [("campaign_id", "=", self.id)],
            "context": {"default_campaign_id": self.id},
        }

    def action_view_assets(self):
        """Open assets for this campaign."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Assets"),
            "res_model": "ipai.asset",
            "view_mode": "kanban,list,form",
            "domain": [("campaign_id", "=", self.id)],
            "context": {
                "default_campaign_id": self.id,
                "default_brand_id": self.brand_id.id,
            },
        }

    def action_view_calendar(self):
        """Open content calendar for this campaign."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Content Calendar"),
            "res_model": "ipai.content.calendar.item",
            "view_mode": "calendar,list,form",
            "domain": [("campaign_id", "=", self.id)],
            "context": {"default_campaign_id": self.id},
        }

    def get_kpi_targets_dict(self):
        """Return KPI targets as Python dict."""
        self.ensure_one()
        try:
            return json.loads(self.kpi_targets or "{}")
        except json.JSONDecodeError:
            return {}
