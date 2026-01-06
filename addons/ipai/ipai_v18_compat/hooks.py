# -*- coding: utf-8 -*-
"""
Odoo 18 Compatibility Hooks

This module provides automatic fixes for Odoo 18 breaking changes:
1. view_mode 'tree' → 'list' migration
2. Kanban view card template detection
"""
import logging
import re

_logger = logging.getLogger(__name__)


def fix_odoo18_views(env):
    """
    Fix Odoo 18 view_mode breaking changes.

    Odoo 18 renamed 'tree' to 'list' in ir.actions.act_window view_mode.
    This function patches all actions that still reference 'tree'.

    Args:
        env: Odoo environment (cr, uid, context)

    Returns:
        int: Number of actions patched
    """
    _logger.info("Starting Odoo 18 view_mode compatibility fix...")

    # Find all actions with 'tree' in view_mode
    actions = env["ir.actions.act_window"].search([
        ("view_mode", "ilike", "tree")
    ])

    patched_count = 0
    for action in actions:
        old_mode = action.view_mode
        # Replace 'tree' with 'list' while preserving other modes
        new_mode = re.sub(r'\btree\b', 'list', old_mode)

        if new_mode != old_mode:
            _logger.info(
                "Patching action %s [%s]: '%s' → '%s'",
                action.id, action.name, old_mode, new_mode
            )
            action.write({"view_mode": new_mode})
            patched_count += 1

    _logger.info(
        "Odoo 18 compatibility fix complete. Patched %d actions.",
        patched_count
    )
    return patched_count


def detect_broken_kanbans(env):
    """
    Detect kanban views missing t-name="card" template.

    Odoo 18 requires kanban views to use t-name="card" instead of
    the old t-name="kanban-box" pattern.

    Args:
        env: Odoo environment

    Returns:
        list: List of view records with potential issues
    """
    _logger.info("Scanning for broken kanban views...")

    broken_views = []
    kanban_views = env["ir.ui.view"].search([
        ("type", "=", "kanban"),
        ("active", "=", True)
    ])

    for view in kanban_views:
        arch = view.arch_db or ""
        # Check for old kanban-box pattern without card template
        if 'kanban-box' in arch and 't-name="card"' not in arch:
            _logger.warning(
                "Kanban view %s [%s] may need t-name='card' template",
                view.id, view.name
            )
            broken_views.append(view)

    _logger.info(
        "Kanban scan complete. Found %d potentially broken views.",
        len(broken_views)
    )
    return broken_views


def post_init_hook(env):
    """
    Post-init hook called when module is installed.

    Automatically runs compatibility fixes on module installation.
    """
    _logger.info("Running ipai_v18_compat post_init_hook...")

    # Fix tree → list in view_mode
    patched = fix_odoo18_views(env)

    # Detect (but don't auto-fix) broken kanbans
    broken = detect_broken_kanbans(env)

    if broken:
        _logger.warning(
            "Found %d kanban views that may need manual fixes. "
            "Check logs for details.",
            len(broken)
        )

    _logger.info(
        "ipai_v18_compat post_init_hook complete. "
        "Patched %d actions, detected %d kanban issues.",
        patched, len(broken)
    )
