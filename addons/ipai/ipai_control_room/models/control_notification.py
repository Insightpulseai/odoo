# -*- coding: utf-8 -*-
"""
Control Room Notification Channel Model
=========================================

Notification routing configuration.
"""

from odoo import api, fields, models


class ControlNotificationChannel(models.Model):
    """
    Control Notification Channel

    Configures how and where notifications are sent
    for control room events.
    """

    _name = "control.notification.channel"
    _description = "Notification Channel"
    _order = "name"

    # Identity
    name = fields.Char(
        string="Channel Name",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # Channel Type
    channel_type = fields.Selection(
        [
            ("email", "Email"),
            ("slack", "Slack"),
            ("mattermost", "Mattermost"),
            ("webhook", "Webhook"),
            ("odoo_chat", "Odoo Chat"),
        ],
        string="Channel Type",
        required=True,
    )

    # Connector
    connector_id = fields.Many2one(
        "control.connector",
        string="Connector",
        help="Connector for external channels (Slack, Mattermost, etc.)",
    )

    # Routing Configuration
    routing_json = fields.Text(
        string="Routing (JSON)",
        help="Channel IDs, recipient lists, filters",
        default="{}",
    )

    # Email-specific
    email_to = fields.Char(
        string="Email To",
        help="Comma-separated email addresses",
    )
    email_cc = fields.Char(
        string="Email CC",
    )
    email_template_id = fields.Many2one(
        "mail.template",
        string="Email Template",
    )

    # Event Filters
    event_filter = fields.Selection(
        [
            ("all", "All Events"),
            ("run_fail", "Pipeline Failures Only"),
            ("dq_fail", "DQ Failures Only"),
            ("critical", "Critical Severity Only"),
            ("custom", "Custom Filter"),
        ],
        string="Event Filter",
        default="all",
    )
    custom_filter_json = fields.Text(
        string="Custom Filter (JSON)",
        help="Custom event filter configuration",
    )

    # Severity Filter
    min_severity = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Minimum Severity",
        default="low",
    )

    # Rate Limiting
    rate_limit_enabled = fields.Boolean(
        string="Rate Limit",
        default=False,
    )
    rate_limit_per_hour = fields.Integer(
        string="Max per Hour",
        default=10,
    )

    # Ownership
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    # Documentation
    description = fields.Text(
        string="Description",
    )

    def action_send_test(self):
        """Send a test notification"""
        self.ensure_one()
        # Placeholder for actual notification sending
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Test Notification",
                "message": f"Test notification sent via {self.channel_type}",
                "type": "success",
            }
        }
