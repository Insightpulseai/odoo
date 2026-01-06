# -*- coding: utf-8 -*-
"""
Control Room Feature Flag Model
=================================

Feature flag management for controlled rollouts.
"""

from odoo import api, fields, models


class ControlFeatureFlag(models.Model):
    """
    Control Feature Flag

    Enables feature toggles at various scopes
    (global, company, project, user).
    """

    _name = "control.feature.flag"
    _description = "Feature Flag"
    _order = "key"

    # Identity
    key = fields.Char(
        string="Flag Key",
        required=True,
        index=True,
        help="Unique identifier (e.g., 'enable_new_dashboard')",
    )
    name = fields.Char(
        string="Flag Name",
        required=True,
    )

    # State
    enabled = fields.Boolean(
        string="Enabled",
        default=False,
    )

    # Scope
    scope = fields.Selection(
        [
            ("global", "Global"),
            ("company", "Company"),
            ("project", "Project"),
            ("user", "User"),
        ],
        string="Scope",
        default="global",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        help="Required if scope is 'company'",
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        help="Required if scope is 'project'",
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        help="Required if scope is 'user'",
    )

    # Configuration
    config_json = fields.Text(
        string="Configuration (JSON)",
        help="Additional flag configuration",
        default="{}",
    )

    # Rollout
    rollout_percentage = fields.Integer(
        string="Rollout (%)",
        default=100,
        help="Percentage of users to enable for (0-100)",
    )

    # Timing
    valid_from = fields.Datetime(
        string="Valid From",
    )
    valid_until = fields.Datetime(
        string="Valid Until",
    )

    # Documentation
    description = fields.Text(
        string="Description",
    )

    _sql_constraints = [
        (
            "key_scope_uniq",
            "UNIQUE(key, scope, company_id, project_id, user_id)",
            "Flag key must be unique per scope",
        )
    ]

    @api.model
    def is_enabled(self, key, company_id=None, project_id=None, user_id=None):
        """
        Check if a feature flag is enabled.

        Checks in order of specificity:
        1. User-specific flag
        2. Project-specific flag
        3. Company-specific flag
        4. Global flag

        Returns True if any matching flag is enabled.
        """
        now = fields.Datetime.now()

        # Build domain for each scope level
        domains = []

        # User scope
        if user_id:
            domains.append([
                ("key", "=", key),
                ("scope", "=", "user"),
                ("user_id", "=", user_id),
            ])

        # Project scope
        if project_id:
            domains.append([
                ("key", "=", key),
                ("scope", "=", "project"),
                ("project_id", "=", project_id),
            ])

        # Company scope
        if company_id:
            domains.append([
                ("key", "=", key),
                ("scope", "=", "company"),
                ("company_id", "=", company_id),
            ])

        # Global scope
        domains.append([
            ("key", "=", key),
            ("scope", "=", "global"),
        ])

        # Check each scope in order
        for domain in domains:
            flag = self.search(domain, limit=1)
            if flag:
                # Check validity period
                if flag.valid_from and now < flag.valid_from:
                    continue
                if flag.valid_until and now > flag.valid_until:
                    continue
                return flag.enabled

        return False

    @api.model
    def get_config(self, key, company_id=None, project_id=None, user_id=None):
        """Get the configuration for a feature flag"""
        import json

        now = fields.Datetime.now()
        domains = []

        if user_id:
            domains.append([("key", "=", key), ("scope", "=", "user"), ("user_id", "=", user_id)])
        if project_id:
            domains.append([("key", "=", key), ("scope", "=", "project"), ("project_id", "=", project_id)])
        if company_id:
            domains.append([("key", "=", key), ("scope", "=", "company"), ("company_id", "=", company_id)])
        domains.append([("key", "=", key), ("scope", "=", "global")])

        for domain in domains:
            flag = self.search(domain, limit=1)
            if flag:
                if flag.valid_from and now < flag.valid_from:
                    continue
                if flag.valid_until and now > flag.valid_until:
                    continue
                try:
                    return json.loads(flag.config_json) if flag.config_json else {}
                except json.JSONDecodeError:
                    return {}

        return {}
