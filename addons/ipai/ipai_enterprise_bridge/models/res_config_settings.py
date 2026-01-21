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

    # ==========================================================================
    # Enterprise Feature Stubs (CE → 19/EE Parity)
    # ==========================================================================
    # These fields exist in Odoo Enterprise but not CE 18.0
    # Stubbed here to prevent view inheritance errors
    # ==========================================================================

    # POS Self-Ordering (Enterprise only)
    pos_self_ordering_mode = fields.Selection(
        [
            ("nothing", "Disabled"),
            ("mobile", "QR Code (Mobile)"),
            ("kiosk", "Self-Ordering Kiosk"),
        ],
        string="Self-Ordering Mode",
        default="nothing",
        config_parameter="ipai_bridge.pos_self_ordering_mode",
        help="[Enterprise Feature Stub] Enable POS self-ordering. "
        "Install OCA alternative: pos_order_mgmt or use IPAI Scout vertical.",
    )
    pos_self_ordering_service_mode = fields.Selection(
        [
            ("counter", "Order at Counter"),
            ("table", "Order at Table"),
        ],
        string="Self-Ordering Service Mode",
        default="counter",
        config_parameter="ipai_bridge.pos_self_ordering_service_mode",
        help="[Enterprise Feature Stub] Service mode for self-ordering.",
    )
    pos_self_ordering_pay_after = fields.Selection(
        [
            ("each", "After Each Order"),
            ("meal", "After Meal"),
        ],
        string="Self-Ordering Payment",
        default="each",
        config_parameter="ipai_bridge.pos_self_ordering_pay_after",
        help="[Enterprise Feature Stub] When customers pay in self-ordering flow.",
    )
    pos_self_ordering_image_home_ids = fields.Many2many(
        "ir.attachment",
        "pos_self_ordering_image_home_rel",
        "config_id",
        "image_id",
        string="Self-Ordering Home Images",
        help="[Enterprise Feature Stub] Images displayed on self-ordering home screen.",
    )
