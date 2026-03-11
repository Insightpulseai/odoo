# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
Post-init hook: seed ir.config_parameter from ACA environment variables.

This hook runs once at module install/upgrade. It reads Azure OpenAI
configuration from container environment variables and writes them into
ir.config_parameter — but only if the DB value is empty or missing.

DB values always take precedence over env vars. This ensures that:
  1. First deploy on ACA auto-configures from Key Vault → env vars.
  2. Manual overrides via Settings UI are never clobbered.
"""
import logging
import os

_logger = logging.getLogger(__name__)

# Mapping: env var name → ir.config_parameter key
_ENV_TO_ICP = {
    "AZURE_OPENAI_BASE_URL": "ipai_ask_ai_azure.base_url",
    "AZURE_OPENAI_API_KEY": "ipai_ask_ai_azure.api_key",
    "AZURE_OPENAI_DEPLOYMENT": "ipai_ask_ai_azure.model",
    "AZURE_OPENAI_API_MODE": "ipai_ask_ai_azure.api_mode",
}

# Default values for optional keys
_DEFAULTS = {
    "AZURE_OPENAI_API_MODE": "responses",
}


def post_init_hook(env):
    """Seed Azure OpenAI config from env vars into ir.config_parameter.

    Only writes if:
      - The env var is set and non-empty.
      - The DB value is empty, missing, or False.
    """
    icp = env["ir.config_parameter"].sudo()
    seeded = []

    for env_var, icp_key in _ENV_TO_ICP.items():
        env_value = os.environ.get(env_var, "").strip()
        if not env_value:
            # Also check defaults for optional keys
            env_value = _DEFAULTS.get(env_var, "")
            if not env_value:
                continue

        existing = icp.get_param(icp_key, default="")
        if existing:
            _logger.debug(
                "Copilot config %s already set in DB, skipping env seed", icp_key
            )
            continue

        icp.set_param(icp_key, env_value)
        # Log the key name but never the value (secrets policy)
        _logger.info(
            "Copilot config seeded: %s ← env(%s)", icp_key, env_var
        )
        seeded.append(icp_key)

    if seeded:
        _logger.info(
            "Copilot post_init_hook: seeded %d config keys: %s",
            len(seeded),
            ", ".join(seeded),
        )
    else:
        _logger.info("Copilot post_init_hook: no config keys needed seeding")
