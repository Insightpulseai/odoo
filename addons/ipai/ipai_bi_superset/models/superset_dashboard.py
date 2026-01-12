# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models


class IpaiBiSupersetDashboard(models.Model):
    """Registry of Superset dashboards available for embedding."""

    _name = "ipai.bi.superset.dashboard"
    _description = "Superset Dashboard"
    _inherit = ["mail.thread"]
    _order = "sequence, name"

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10)
    slug = fields.Char(
        required=True,
        index=True,
        help="URL slug for the dashboard",
    )
    superset_id = fields.Char(
        index=True,
        help="Dashboard ID in Superset",
    )

    # Instance relationship
    instance_id = fields.Many2one(
        "ipai.bi.superset.instance",
        required=True,
        index=True,
        ondelete="cascade",
    )

    # Dataset relationships
    dataset_ids = fields.Many2many(
        "ipai.bi.superset.dataset",
        "ipai_bi_dataset_dashboard_rel",
        "dashboard_id",
        "dataset_id",
        string="Datasets",
    )

    # Embed configuration
    default_filters_json = fields.Text(
        help="Default filter configuration as JSON",
    )
    standalone_mode = fields.Boolean(
        default=True,
        help="Embed in standalone mode (no Superset chrome)",
    )

    # Access control
    embed_allowed_groups = fields.Many2many(
        "res.groups",
        "ipai_bi_dashboard_group_rel",
        "dashboard_id",
        "group_id",
        string="Allowed Groups",
        help="Groups allowed to view this embedded dashboard",
    )
    public_access = fields.Boolean(
        default=False,
        help="Allow public (unauthenticated) access",
    )

    # Metadata
    description = fields.Text()
    thumbnail = fields.Binary(
        attachment=True,
        help="Dashboard thumbnail image",
    )
    last_synced = fields.Datetime(
        readonly=True,
        help="Last metadata sync from Superset",
    )

    # Ownership
    company_id = fields.Many2one(
        related="instance_id.company_id",
        store=True,
        index=True,
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "unique_slug_instance",
            "UNIQUE(slug, instance_id)",
            "Dashboard slug must be unique per instance",
        ),
    ]

    def get_embed_url(self, filters=None):
        """Generate embed URL for this dashboard.

        Args:
            filters: Optional dict of additional filter parameters

        Returns:
            str: Full embed URL
        """
        self.ensure_one()

        # Merge default filters with provided filters
        all_filters = {}
        if self.default_filters_json:
            try:
                all_filters = json.loads(self.default_filters_json)
            except json.JSONDecodeError:
                pass
        if filters:
            all_filters.update(filters)

        return self.instance_id.get_embed_url(
            self.superset_id or self.slug,
            filters=all_filters if all_filters else None,
        )

    def action_open_dashboard(self):
        """Open dashboard in new tab."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.get_embed_url(),
            "target": "new",
        }

    def action_sync_metadata(self):
        """Sync dashboard metadata from Superset.

        This is a placeholder for async sync via queue_job.
        """
        self.ensure_one()
        self.last_synced = fields.Datetime.now()
        return True
