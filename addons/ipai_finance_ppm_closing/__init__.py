# -*- coding: utf-8 -*-
import json
import logging
from pathlib import Path

from odoo import SUPERUSER_ID, api

from . import models

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Post-installation hook to load seed JSON into ir.config_parameter.

    Only loads if the parameter doesn't already exist, preserving any
    manual customizations.
    """
    ICP = env["ir.config_parameter"].sudo()
    param_key = "ipai.close.seed_json"

    # Check if already configured
    existing = ICP.get_param(param_key)
    if existing:
        _logger.info(
            "Seed JSON already configured in ir.config_parameter, skipping load."
        )
        return

    # Load seed from file
    seed_file = Path(__file__).parent / "seed" / "closing_v1_2_0.json"
    if not seed_file.exists():
        _logger.warning("Seed file not found: %s", seed_file)
        return

    try:
        seed_json = seed_file.read_text()
        # Validate it's valid JSON
        json.loads(seed_json)
        ICP.set_param(param_key, seed_json)
        _logger.info(
            "Loaded seed JSON into ir.config_parameter '%s' (%d bytes)",
            param_key,
            len(seed_json),
        )
    except json.JSONDecodeError as e:
        _logger.error("Invalid seed JSON: %s", e)
    except Exception as e:
        _logger.error("Failed to load seed JSON: %s", e)
