# -*- coding: utf-8 -*-
"""
Post-migration script for ipai_v18_compat module upgrade.

This script runs after the module is upgraded, ensuring that any new
actions introduced by other module upgrades also get patched.
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Post-migration hook for module upgrade.

    Re-runs the view_mode fix to catch any new actions that may have
    been introduced by other module installations/upgrades.
    """
    _logger.info(
        "Running ipai_v18_compat post-migration from version %s",
        version
    )

    # Import here to ensure Odoo environment is available
    from odoo import api, SUPERUSER_ID
    from odoo.addons.ipai_v18_compat.hooks import (
        fix_odoo18_views,
        detect_broken_kanbans
    )

    env = api.Environment(cr, SUPERUSER_ID, {})

    # Run fixes
    patched = fix_odoo18_views(env)
    broken = detect_broken_kanbans(env)

    _logger.info(
        "ipai_v18_compat post-migration complete. "
        "Patched %d actions, detected %d kanban issues.",
        patched, len(broken)
    )
