# -*- coding: utf-8 -*-
"""
Odoo 18 Compatibility Hooks

This module provides automatic fixes for Odoo 18 breaking changes:
1. view_mode 'tree' → 'list' migration
2. Kanban view card template detection and optional deactivation
"""
import logging

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
    ActWindow = env["ir.actions.act_window"].sudo()
    actions = ActWindow.search([("view_mode", "ilike", "tree")])

    patched_count = 0
    for action in actions:
        # Parse comma-separated modes
        modes = [m.strip() for m in (action.view_mode or "").split(",") if m.strip()]
        if not modes:
            continue

        # Replace 'tree' with 'list'
        new_modes = ["list" if m == "tree" else m for m in modes]

        if new_modes != modes:
            new_mode_str = ",".join(new_modes)
            _logger.info(
                "Patching action %s [%s]: '%s' → '%s'",
                action.id, action.name, action.view_mode, new_mode_str
            )
            action.write({"view_mode": new_mode_str})
            patched_count += 1

    _logger.info(
        "Odoo 18 compatibility fix complete. Patched %d actions.",
        patched_count
    )
    return patched_count


def detect_broken_kanbans(env):
    """
    Detect kanban views missing t-name="card" template.

    Odoo 18 requires kanban views to have a t-name="card" template.
    Views missing this template will cause KanbanArchParser errors.

    Args:
        env: Odoo environment

    Returns:
        list: List of view records with potential issues
    """
    _logger.info("Scanning for broken kanban views...")

    View = env["ir.ui.view"].sudo()
    kanban_views = View.search([
        ("type", "=", "kanban"),
        ("active", "=", True)
    ])

    broken_views = []
    for view in kanban_views:
        arch = view.arch_db or ""
        # Check for missing card template (both quote styles)
        if 't-name="card"' not in arch and "t-name='card'" not in arch:
            _logger.warning(
                "Kanban view %s [%s] model=%s may need t-name='card' template",
                view.id, view.name, view.model
            )
            broken_views.append(view)

    _logger.info(
        "Kanban scan complete. Found %d potentially broken views.",
        len(broken_views)
    )
    return broken_views


def deactivate_broken_views(env, views):
    """
    Deactivate broken views to prevent UI crashes.

    This is a safety measure - it's better to have missing views than
    crashing UI. The views can be patched and reactivated later.

    Args:
        env: Odoo environment
        views: List of view records to deactivate

    Returns:
        int: Number of views deactivated
    """
    if not views:
        return 0

    view_ids = [v.id for v in views]
    env["ir.ui.view"].sudo().browse(view_ids).write({"active": False})
    _logger.warning("Deactivated %d broken kanban views", len(views))
    return len(views)


def post_init_hook(env):
    """
    Post-init hook called when module is installed.

    Automatically runs compatibility fixes on module installation.

    To enable automatic deactivation of broken kanban views, set:
        Settings → Technical → Parameters → System Parameters
        key: ipai_v18_compat.deactivate_broken_kanban = 1
    """
    _logger.info("Running ipai_v18_compat post_init_hook...")

    # Fix tree → list in view_mode
    patched = fix_odoo18_views(env)

    # Detect broken kanbans
    broken = detect_broken_kanbans(env)

    # Check if auto-deactivation is enabled via system parameter
    deactivate = env["ir.config_parameter"].sudo().get_param(
        "ipai_v18_compat.deactivate_broken_kanban"
    ) in ("1", "true", "True")

    deactivated = 0
    if deactivate and broken:
        deactivated = deactivate_broken_views(env, broken)
    elif broken:
        _logger.warning(
            "Found %d kanban views that may need manual fixes. "
            "Set system parameter 'ipai_v18_compat.deactivate_broken_kanban=1' "
            "to auto-deactivate. Check logs for details.",
            len(broken)
        )

    # Clear registry cache
    env.registry.clear_cache()

    _logger.info(
        "ipai_v18_compat post_init_hook complete. "
        "Patched %d actions, found %d kanban issues, deactivated %d views.",
        patched, len(broken), deactivated
    )
