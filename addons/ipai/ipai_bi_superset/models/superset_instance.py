# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiBiSupersetInstance(models.Model):
    """Superset instance configuration for JWT-based embedding."""

    _name = "ipai.bi.superset.instance"
    _description = "Superset Instance"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    code = fields.Char(
        required=True,
        index=True,
        help="Technical identifier (e.g., 'prod', 'staging')",
    )
    base_url = fields.Char(
        required=True,
        help="Superset base URL (e.g., https://superset.insightpulseai.net)",
    )

    # JWT configuration
    jwt_audience = fields.Char(
        help="JWT audience claim for guest tokens",
    )
    jwt_user = fields.Char(
        help="Service user name for guest token generation",
    )
    jwt_role = fields.Char(
        default="Gamma",
        help="Superset role for guest tokens (e.g., Gamma, Public)",
    )
    env_key_name = fields.Char(
        default="SUPERSET_JWT_SECRET",
        help="Environment variable name containing JWT secret",
    )

    # Ownership
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    active = fields.Boolean(default=True)
    is_default = fields.Boolean(
        default=False,
        help="Default instance for this company",
    )

    # Related records
    dashboard_ids = fields.One2many(
        "ipai.bi.superset.dashboard",
        "instance_id",
        string="Dashboards",
    )
    dashboard_count = fields.Integer(
        compute="_compute_dashboard_count",
        store=True,
    )
    dataset_ids = fields.One2many(
        "ipai.bi.superset.dataset",
        "instance_id",
        string="Datasets",
    )
    dataset_count = fields.Integer(
        compute="_compute_dataset_count",
        store=True,
    )

    @api.depends("dashboard_ids")
    def _compute_dashboard_count(self):
        for rec in self:
            rec.dashboard_count = len(rec.dashboard_ids)

    @api.depends("dataset_ids")
    def _compute_dataset_count(self):
        for rec in self:
            rec.dataset_count = len(rec.dataset_ids)

    @api.constrains("is_default", "company_id")
    def _check_single_default(self):
        """Ensure only one default instance per company."""
        for rec in self:
            if rec.is_default:
                others = self.search([
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("is_default", "=", True),
                ], limit=1)
                if others:
                    others.is_default = False

    @api.model
    def get_default(self, company_id=None):
        """Get the default active instance for a company."""
        company = (
            self.env["res.company"].browse(company_id)
            if company_id
            else self.env.company
        )
        rec = self.search([
            ("company_id", "=", company.id),
            ("is_default", "=", True),
            ("active", "=", True),
        ], limit=1)
        if rec:
            return rec
        return self.search([
            ("company_id", "=", company.id),
            ("active", "=", True),
        ], limit=1)

    def get_embed_url(self, dashboard_id, filters=None):
        """Generate embed URL for a dashboard with optional filters.

        Args:
            dashboard_id: Superset dashboard ID or slug
            filters: Optional dict of filter parameters

        Returns:
            str: Full embed URL with query parameters
        """
        self.ensure_one()
        url = f"{self.base_url}/superset/dashboard/{dashboard_id}/?standalone=1"
        if filters:
            import urllib.parse
            filter_str = urllib.parse.urlencode(filters)
            url = f"{url}&{filter_str}"
        return url
