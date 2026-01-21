# -*- coding: utf-8 -*-
"""
Control Room Connector Model
=============================

External system integration definitions.
"""

from odoo import api, fields, models


class ControlConnector(models.Model):
    """
    Control Connector

    Defines an external system integration.
    Configuration is stored without secrets;
    secrets are referenced via control.secret.ref.
    """

    _name = "control.connector"
    _description = "Control Connector"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    # Identity
    name = fields.Char(
        string="Connector Name",
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string="Code",
        index=True,
        help="Unique identifier for API use",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # Connector Type
    connector_type = fields.Selection(
        [
            ("postgres", "PostgreSQL"),
            ("supabase", "Supabase"),
            ("s3", "AWS S3 / Object Storage"),
            ("gdrive", "Google Drive"),
            ("slack", "Slack"),
            ("http", "HTTP/REST API"),
            ("odoo_rpc", "Odoo RPC"),
            ("mattermost", "Mattermost"),
            ("n8n", "n8n Webhook"),
            ("superset", "Apache Superset"),
            ("databricks", "Databricks"),
            ("bigquery", "BigQuery"),
            ("snowflake", "Snowflake"),
            ("custom", "Custom"),
        ],
        string="Connector Type",
        required=True,
        tracking=True,
    )

    # Configuration
    config_json = fields.Text(
        string="Configuration (JSON)",
        help="Non-secret configuration (host, port, database, etc.)",
    )
    host = fields.Char(
        string="Host",
        help="Connection host/endpoint",
    )
    port = fields.Integer(
        string="Port",
    )
    database = fields.Char(
        string="Database/Schema",
    )

    # Secrets Reference
    secret_ref_id = fields.Many2one(
        "control.secret.ref",
        string="Secret Reference",
        help="Reference to secrets backend",
    )

    # Company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    # Health Status
    last_health_at = fields.Datetime(
        string="Last Health Check",
    )
    last_health_status = fields.Selection(
        [
            ("ok", "OK"),
            ("warn", "Warning"),
            ("error", "Error"),
            ("unknown", "Unknown"),
        ],
        string="Health Status",
        default="unknown",
    )
    health_message = fields.Text(
        string="Health Message",
    )

    # Documentation
    description = fields.Text(
        string="Description",
    )

    _sql_constraints = [
        (
            "code_company_uniq",
            "UNIQUE(code, company_id)",
            "Connector code must be unique per company",
        )
    ]

    def action_test_connection(self):
        """Test the connector connection"""
        self.ensure_one()
        # Placeholder for actual connection test logic
        self.write(
            {
                "last_health_at": fields.Datetime.now(),
                "last_health_status": "ok",
                "health_message": "Connection test successful (placeholder)",
            }
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Connection Test",
                "message": "Connection test completed.",
                "type": "success",
            },
        }
