# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Idempotent seeding of defaults for enterprise bridge.

    This hook runs after module installation to set up:
    - Default system parameters for Supabase/AI integration
    - Default policy records
    - Default close checklist templates
    """
    _logger.info("IPAI Enterprise Bridge: Running post_init_hook")

    # Set default system parameters (only if not already set)
    IrConfigParameter = env["ir.config_parameter"].sudo()

    defaults = {
        "ipai_bridge.supabase_url": "",
        "ipai_bridge.supabase_anon_key": "",
        "ipai_bridge.ai_endpoint_url": "",
        "ipai_bridge.enable_scout": "False",
        "ipai_bridge.enable_ces": "False",
        "ipai_bridge.enable_retail_sync": "False",
        "ipai_bridge.enable_project_sync": "False",
    }

    for key, default_value in defaults.items():
        if not IrConfigParameter.get_param(key):
            IrConfigParameter.set_param(key, default_value)

    _logger.info("IPAI Enterprise Bridge: post_init_hook completed")
