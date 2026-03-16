# -*- coding: utf-8 -*-
"""
Configuration Settings for Superset Connector
"""
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Default Superset Connection
    superset_connection_id = fields.Many2one(
        "superset.connection",
        string="Default Superset Connection",
        config_parameter="ipai_superset_connector.default_connection_id",
    )

    # Auto-sync settings
    superset_auto_sync = fields.Boolean(
        string="Enable Auto-Sync",
        config_parameter="ipai_superset_connector.auto_sync",
        default=False,
    )
    superset_sync_interval = fields.Selection(
        [
            ("hourly", "Hourly"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
        ],
        string="Sync Interval",
        config_parameter="ipai_superset_connector.sync_interval",
        default="daily",
    )

    # Analytics Views
    superset_create_analytics_views = fields.Boolean(
        string="Create Pre-built Analytics Views",
        config_parameter="ipai_superset_connector.create_analytics_views",
        default=True,
    )

    # Security
    superset_enable_rls = fields.Boolean(
        string="Enable Row-Level Security",
        config_parameter="ipai_superset_connector.enable_rls",
        default=True,
        help="Filter data by company_id for multi-tenant access",
    )

    def action_create_all_analytics_views(self):
        """Create all pre-built analytics views"""
        AnalyticsView = self.env["superset.analytics.view"]
        created, errors = AnalyticsView.create_all_views()

        message = f"{created} analytics views created."
        if errors:
            message += f"\n\nErrors:\n" + "\n".join(errors)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Analytics Views",
                "message": message,
                "type": "warning" if errors else "success",
                "sticky": bool(errors),
            },
        }
