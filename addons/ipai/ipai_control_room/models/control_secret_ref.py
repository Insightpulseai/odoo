# -*- coding: utf-8 -*-
"""
Control Room Secret Reference Model
=====================================

Reference pointers to external secret managers.
Secrets are NOT stored in Odoo.
"""

from odoo import fields, models


class ControlSecretRef(models.Model):
    """
    Control Secret Reference

    Stores references to secrets in external secret managers.
    The actual secrets are never stored in Odoo.
    """

    _name = "control.secret.ref"
    _description = "Secret Reference"
    _order = "name"

    # Identity
    name = fields.Char(
        string="Secret Name",
        required=True,
    )

    # Provider
    provider = fields.Selection(
        [
            ("odoo_system_param", "Odoo System Parameter"),
            ("vault", "HashiCorp Vault"),
            ("aws_secrets", "AWS Secrets Manager"),
            ("supabase", "Supabase Vault"),
            ("do_secrets", "DigitalOcean App Secrets"),
            ("gcp_secrets", "GCP Secret Manager"),
            ("azure_keyvault", "Azure Key Vault"),
            ("env_var", "Environment Variable"),
        ],
        string="Provider",
        required=True,
        default="env_var",
    )

    # Reference Key
    ref_key = fields.Char(
        string="Reference Key",
        required=True,
        help="Key/path in the secret manager (NOT the secret value)",
    )

    # Metadata
    secret_type = fields.Selection(
        [
            ("api_key", "API Key"),
            ("password", "Password"),
            ("token", "Token"),
            ("certificate", "Certificate"),
            ("connection_string", "Connection String"),
            ("other", "Other"),
        ],
        string="Secret Type",
        default="api_key",
    )

    # Rotation
    last_rotated_at = fields.Datetime(
        string="Last Rotated At",
    )
    rotation_period_days = fields.Integer(
        string="Rotation Period (days)",
        help="Recommended rotation period",
    )

    # Access
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    # Documentation
    notes = fields.Text(
        string="Notes",
        help="Usage notes (NOT the secret value)",
    )

    # Related
    connector_ids = fields.One2many(
        "control.connector",
        "secret_ref_id",
        string="Used By Connectors",
    )

    _sql_constraints = [
        (
            "provider_ref_uniq",
            "UNIQUE(provider, ref_key, company_id)",
            "Secret reference must be unique per provider and company",
        )
    ]
