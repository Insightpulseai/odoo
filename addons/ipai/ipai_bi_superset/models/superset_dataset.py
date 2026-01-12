# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiBiSupersetDataset(models.Model):
    """Represents Odoo-owned Supabase tables/views exposed to Superset."""

    _name = "ipai.bi.superset.dataset"
    _description = "Superset Dataset"
    _order = "database_name, technical_name"

    name = fields.Char(required=True)
    technical_name = fields.Char(
        required=True,
        index=True,
        help="Full table/view name (e.g., schema.table_name)",
    )
    database_name = fields.Char(
        help="Database/schema tier (e.g., scout_bronze, scout_silver, scout_gold)",
    )

    # Superset relationship
    instance_id = fields.Many2one(
        "ipai.bi.superset.instance",
        required=True,
        index=True,
        ondelete="cascade",
    )
    superset_id = fields.Integer(
        help="Dataset ID in Superset (if synced)",
    )

    # Odoo mapping
    odoo_model_id = fields.Many2one(
        "ir.model",
        string="Odoo Model",
        help="If this dataset maps back to an Odoo model",
    )

    # Metadata
    description = fields.Text()
    is_materialized = fields.Boolean(
        default=False,
        help="True if this is a materialized view",
    )
    refresh_schedule = fields.Char(
        help="Cron schedule for refresh (if materialized)",
    )
    row_count = fields.Integer(
        readonly=True,
        help="Approximate row count (from last sync)",
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

    # Dashboard relationship
    dashboard_ids = fields.Many2many(
        "ipai.bi.superset.dashboard",
        "ipai_bi_dataset_dashboard_rel",
        "dataset_id",
        "dashboard_id",
        string="Used in Dashboards",
    )

    _sql_constraints = [
        (
            "unique_technical_name_instance",
            "UNIQUE(technical_name, instance_id)",
            "Dataset technical name must be unique per instance",
        ),
    ]

    @api.depends("technical_name", "database_name")
    def _compute_display_name(self):
        for rec in self:
            if rec.database_name:
                rec.display_name = f"{rec.database_name}.{rec.technical_name}"
            else:
                rec.display_name = rec.technical_name
