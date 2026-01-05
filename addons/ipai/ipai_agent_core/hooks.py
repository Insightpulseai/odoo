# -*- coding: utf-8 -*-
"""Post-init hook to load skillpack from JSON files."""

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Load skillpack JSON into database on module install."""
    try:
        from .models.skillpack_loader import load_skillpack_from_default_paths

        load_skillpack_from_default_paths(env)
        _logger.info("IPAI Agent Core: Skillpack loaded successfully")
    except Exception as e:
        _logger.warning("IPAI Agent Core: Could not load skillpack: %s", e)
