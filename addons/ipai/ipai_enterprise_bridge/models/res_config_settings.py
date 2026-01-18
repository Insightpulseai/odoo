# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Supabase integration settings
    ipai_supabase_url = fields.Char(
        string="Supabase URL",
        config_parameter="ipai_bridge.supabase_url",
        help="Supabase project URL for external integrations",
    )
    ipai_supabase_anon_key = fields.Char(
        string="Supabase Anon Key",
        config_parameter="ipai_bridge.supabase_anon_key",
        help="Supabase anonymous key for public API access",
    )

    # AI integration settings
    ipai_ai_endpoint_url = fields.Char(
        string="AI Endpoint URL",
        config_parameter="ipai_bridge.ai_endpoint_url",
        help="URL for AI inference endpoint (n8n/Edge Functions)",
    )

    # Vertical toggles
    ipai_enable_scout = fields.Boolean(
        string="Enable Scout (Retail)",
        config_parameter="ipai_bridge.enable_scout",
        help="Enable Scout retail intelligence features",
    )
    ipai_enable_ces = fields.Boolean(
        string="Enable CES (Creative Ops)",
        config_parameter="ipai_bridge.enable_ces",
        help="Enable CES creative effectiveness features",
    )

    # Sync toggles
    ipai_enable_retail_sync = fields.Boolean(
        string="Enable Retail Sync",
        config_parameter="ipai_bridge.enable_retail_sync",
        help="Enable POS/inventory event sync to Supabase",
    )
    ipai_enable_project_sync = fields.Boolean(
        string="Enable Project Sync",
        config_parameter="ipai_bridge.enable_project_sync",
        help="Enable project/task event sync to Supabase",
    )
